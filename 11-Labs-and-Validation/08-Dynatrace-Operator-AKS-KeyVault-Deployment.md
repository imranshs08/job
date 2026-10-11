# Lab 08: Enterprise Dynatrace Operator & DynaKube Deployment on AKS via Azure Key Vault CSI Driver

> **Target Tenant:** [Dynatrace SaaS Tenant UI (ybl31832)](https://ybl31832.apps.dynatrace.com/ui)  
> **API Endpoint:** `https://ybl31832.apps.dynatrace.com/api/v1`  
> **Target Cluster:** `aks-agc-lab-spot` (via `16-Automation-Scripts/azure_agc_lab_manager.sh`)  
> **Operator Version:** `v1.11.0` (Official Kubernetes release manifest)  
> **DynaKube API:** `dynatrace.com/v1beta6` (Latest stable Custom Resource API)  
> **Security Standard:** Zero-Trust Secret Rotation with Azure Key Vault & Secrets Store CSI Driver

---

## 🏛️ Executive Architecture & "The Why"

In modern enterprise Kubernetes clusters, hardcoding sensitive observability tokens directly in declarative Git repositories (GitOps) or using static Kubernetes Secrets violates compliance standards (SOC 2, ISO 27001, CIS Benchmarks).

### The Architectural Blueprint:
```
                               +------------------------------------------+
                               |         Azure Key Vault (AKV)            |
                               |   • dynatrace-api-token                  |
                               |   • dynatrace-data-ingest-token          |
                               +--------------------+---------------------+
                                                    |
                                    User-Assigned Managed Identity
                                      (Least-Privilege Secret GET)
                                                    |
                               +--------------------v---------------------+
                               |    Secrets Store CSI Driver (AKS)        |
                               |     SecretProviderClass (dynatrace)      |
                               +--------------------+---------------------+
                                                    | Auto-sync (secretObjects)
                               +--------------------v---------------------+
                               |        Native K8s Secret: "dynakube"     |
                               |          Namespace: dynatrace            |
                               |     - apiToken: <decrypted>              |
                               |     - dataIngestToken: <decrypted>       |
                               +--------------------+---------------------+
                                                    |
                               +--------------------v---------------------+
                               |         Dynatrace Operator v1.11.0       |
                               |         (Watches DynaKube CRDs)          |
                               +--------------------+---------------------+
                                                    |
                           +------------------------+------------------------+
                           |                                                 |
            +--------------v--------------+                   +--------------v--------------+
            |      OneAgent DaemonSet     |                   |  Containerized ActiveGate   |
            |  (CloudNativeFullStack)     |                   |   (Routing & K8s Metrics)   |
            +--------------+--------------+                   +--------------+--------------+
                           |                                                 |
                           +------------------------+------------------------+
                                                    | TLS 1.3 Outbound (Port 443)
                                                    v
                               +------------------------------------------+
                               | Dynatrace SaaS Tenant                    |
                               | https://ybl31832.apps.dynatrace.com      |
                               +------------------------------------------+
```

### Why Secrets Store CSI Driver Sync?
The Dynatrace Operator expects a native Kubernetes Secret (`dynakube`) containing the keys `apiToken` and `dataIngestToken`. The **Azure Key Vault Secrets Store CSI Driver** allows us to:
1. Maintain Azure Key Vault as the **single source of truth** for all credentials.
2. Automatically project secrets into Kubernetes memory without storing secrets in version control.
3. Use Azure Managed Identities (`az identity`) without having to manage static Azure Service Principal client secrets.

---

## 🎯 Lab Objectives
1. **Provision AKS Infrastructure**: Spin up an ultra-cost-effective Spot cluster (`aks-agc-lab-spot`) with OIDC and Workload Identity enabled.
2. **Generate Scoped API Tokens**: Create an operator token and metrics ingestion token in Dynatrace SaaS.
3. **Configure Azure Key Vault**: Securely inject tokens into AKV and bind AKS Managed Identity access policies.
4. **Deploy SecretProviderClass**: Automatically materialize the `dynakube` Kubernetes Secret via Secrets Store CSI.
5. **Deploy Dynatrace Operator v1.11.0**: Install using pure Kubernetes YAML manifests (no Helm dependency).
6. **Deploy DynaKube `v1beta6`**: Apply the latest Custom Resource specification for full cloud-native stack observability.
7. **Production Verification & SRE Troubleshooting**: Inspect container injection, OneAgent DaemonSets, and live SaaS telemetry.

---

## 🛠️ Step-by-Step Execution Guide

### Step 1: Provisioning the AKS Infrastructure

Execute the remote automation manager to create the cluster with Workload Identity and modern Azure network providers:

```bash
# 1. Spin up the lab cluster (~3-5 mins)
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_agc_lab_manager.sh" | bash -s -- up

# 2. Set environment parameters
export RG_NAME="rg-gateway-api-lab"
export CLUSTER_NAME="aks-agc-lab-spot"
export LOCATION="centralus"
export DT_TENANT_API="https://ybl31832.apps.dynatrace.com/api/v1"
export KV_NAME="kv-dt-lab-$RANDOM"  # Globally unique Key Vault name

# 3. Pull cluster credentials to local Kubeconfig
az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing

# 4. Verify cluster nodes are Ready
kubectl get nodes -o wide
```

---

### Step 2: Harvesting Dynatrace SaaS Tokens

1. Navigate to **[Dynatrace UI (ybl31832)](https://ybl31832.apps.dynatrace.com/ui)**.
2. Open the navigation menu and choose **Manage** > **Access tokens**.
3. Click **Generate new token**:
   * **Token Name:** `k8s-operator-token`
   * **Required Scopes:**
     * `InstallerDownload`: Allows the operator to download OneAgent and ActiveGate container images and binaries.
     * `DataExport`: Allows querying telemetry.
     * `ReadConfig`: Allows reading monitoring settings.
     * `WriteConfig`: Allows automatic configuration updates.
     * `activeGates.read` & `activeGates.write`: Enables ActiveGate lifecycle management.
   * Click **Generate** and store the token string securely.
4. Generate the **Data Ingest Token**:
   * **Token Name:** `k8s-data-ingest-token`
   * **Scope:** `metrics.ingest`
   * Click **Generate** and store the token string securely.

---

### Step 3: Azure Key Vault Provisioning & Secret Storage

```bash
# 1. Create dedicated Azure Key Vault within the lab Resource Group
az keyvault create \
  --name "$KV_NAME" \
  --resource-group "$RG_NAME" \
  --location "$LOCATION" \
  --enable-rbac-authorization false

# 2. Store the API Token inside Key Vault
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-api-token" \
  --value "<YOUR_DYNATRACE_API_TOKEN>"

# 3. Store the Data Ingest Token inside Key Vault
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-data-ingest-token" \
  --value "<YOUR_DYNATRACE_DATA_INGEST_TOKEN>"
```

---

### Step 4: Secrets Store CSI Driver & SecretProviderClass Setup

```bash
# 1. Enable Azure Key Vault Secrets Provider addon on AKS
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name "$CLUSTER_NAME" \
  --resource-group "$RG_NAME"

# 2. Extract the User-Assigned Managed Identity created for the CSI driver
CSI_IDENTITY_CLIENT_ID=$(az aks show \
  --resource-group "$RG_NAME" \
  --name "$CLUSTER_NAME" \
  --query "addonProfiles.azureKeyvaultSecretsProvider.identity.clientId" \
  -o tsv)

# 3. Grant 'GET' and 'LIST' secret access to the CSI Identity
az keyvault set-policy \
  --name "$KV_NAME" \
  --secret-permissions get list \
  --spn "$CSI_IDENTITY_CLIENT_ID"

AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)

# 4. Create the target namespace
kubectl create namespace dynatrace
```

#### Apply the SecretProviderClass Manifest (with Comments):
```yaml
# secretproviderclass.yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: dynatrace-kv-sync
  namespace: dynatrace
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"                      # Authenticate via node VM managed identity
    userAssignedIdentityID: "<CSI_IDENTITY_CLIENT_ID>" # User-assigned client ID
    keyvaultName: "<KV_NAME>"
    cloudName: ""
    objects: |
      array:
        - |
          objectName: dynatrace-api-token
          objectType: secret
          objectVersion: ""
        - |
          objectName: dynatrace-data-ingest-token
          objectType: secret
          objectVersion: ""
    tenantId: "<AZURE_TENANT_ID>"
  secretObjects:                                      # CRITICAL: Maps Key Vault objects to K8s Secret
  - secretName: dynakube                              # Target secret name expected by DynaKube CR
    type: Opaque
    data:
    - objectName: dynatrace-api-token
      key: apiToken                                   # Key expected by DynaKube
    - objectName: dynatrace-data-ingest-token
      key: dataIngestToken                            # Key expected by DynaKube
```

Apply via shell expansion:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: dynatrace-kv-sync
  namespace: dynatrace
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "$CSI_IDENTITY_CLIENT_ID"
    keyvaultName: "$KV_NAME"
    cloudName: ""
    objects: |
      array:
        - |
          objectName: dynatrace-api-token
          objectType: secret
          objectVersion: ""
        - |
          objectName: dynatrace-data-ingest-token
          objectType: secret
          objectVersion: ""
    tenantId: "$AZURE_TENANT_ID"
  secretObjects:
  - secretName: dynakube
    type: Opaque
    data:
    - objectName: dynatrace-api-token
      key: apiToken
    - objectName: dynatrace-data-ingest-token
      key: dataIngestToken
EOF
```

#### Materialize the Secret with an Inline Helper Pod:
> **⚠️ SRE Gotcha:** The Secrets Store CSI driver does not create the Kubernetes Secret on `kubectl apply`. Secrets are mounted and synchronized **only when at least one Pod mounts the CSI volume**. We deploy a lightweight pause helper to satisfy this requirement:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dt-secret-sync-helper
  namespace: dynatrace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dt-secret-sync
  template:
    metadata:
      labels:
        app: dt-secret-sync
    spec:
      containers:
      - name: pause
        image: mcr.microsoft.com/oss/kubernetes/pause:3.9
        volumeMounts:
        - name: secrets-store-inline
          mountPath: "/mnt/secrets-store"
          readOnly: true
      volumes:
      - name: secrets-store-inline
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "dynatrace-kv-sync"
EOF

# Verify secret creation:
kubectl get secret dynakube -n dynatrace -o yaml
```

---

### Step 5: Install Dynatrace Operator via Pure YAML Manifests

Deploy the official stable `v1.11.0` release manifests (with CSI driver support for caching OneAgent binaries):

```bash
# 1. Apply the official release YAML manifests directly from GitHub
kubectl apply -f https://github.com/Dynatrace/dynatrace-operator/releases/download/v1.11.0/kubernetes-csi.yaml

# 2. Wait for operator pod readiness in namespace 'dynatrace'
kubectl wait --namespace dynatrace \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=dynatrace-operator \
  --timeout=300s
```

---

### Step 6: Deploy DynaKube Custom Resource (API: `dynatrace.com/v1beta6`)

Apply the `DynaKube` Custom Resource using the latest supported beta API version (`v1beta6`):

```yaml
# dynakube.yaml
apiVersion: dynatrace.com/v1beta6
kind: DynaKube
metadata:
  name: dynakube
  namespace: dynatrace
  annotations:
    # Enables node-level CSI caching for OneAgent code modules
    feature.dynatrace.com/csi-daemonset: "true"
spec:
  # Dynatrace SaaS Tenant API endpoint
  apiUrl: "https://ybl31832.apps.dynatrace.com/api/v1"

  # Points to the K8s Secret populated from Azure Key Vault
  tokens: "dynakube"

  # CloudNativeFullStack: Performs automatic container injection via webhook
  # and deploys OneAgent DaemonSet on all nodes for OS/host-level telemetry.
  oneAgent:
    cloudNativeFullStack: {}

  # Containerized ActiveGate: Automatically monitors the Kubernetes API server
  # (workload health, events, quotas) and acts as an outbound telemetry proxy.
  activeGate:
    capabilities:
      - routing
      - kubernetes-monitoring
```

Command to apply:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: dynatrace.com/v1beta6
kind: DynaKube
metadata:
  name: dynakube
  namespace: dynatrace
  annotations:
    feature.dynatrace.com/csi-daemonset: "true"
spec:
  apiUrl: "https://ybl31832.apps.dynatrace.com/api/v1"
  tokens: "dynakube"
  oneAgent:
    cloudNativeFullStack: {}
  activeGate:
    capabilities:
      - routing
      - kubernetes-monitoring
EOF
```

---

### Step 7: Verification & Health Checks

```bash
# 1. Verify DynaKube status (Transitions from 'Deploying' to 'Running')
kubectl get dynakube -n dynatrace

# 2. Check all pods across the dynatrace namespace
kubectl get pods -n dynatrace -o wide

# Expected pods:
# - dynatrace-operator-xxxxxxxxxx-xxxxx       (Operator controller)
# - dynatrace-webhook-xxxxxxxxxx-xxxxx        (Admission mutation webhook)
# - dynakube-oneagent-csi-xxxxx               (CSI storage provider)
# - dynakube-oneagent-xxxxx                   (OneAgent DaemonSet on each node)
# - dynakube-activegate-0                     (ActiveGate StatefulSet)
# - dt-secret-sync-helper-xxxxxxxxxx-xxxxx    (Key Vault Secret sync trigger)

# 3. Check DaemonSet rollout status
kubectl rollout status daemonset/dynakube-oneagent -n dynatrace

# 4. View real-time Operator reconciliation logs
kubectl logs -n dynatrace -l app.kubernetes.io/name=dynatrace-operator --tail=50 -f
```

### Dynatrace UI Verification:
1. Navigate to **`https://ybl31832.apps.dynatrace.com/ui`**.
2. Select **Kubernetes** from the left navigation bar.
3. Locate **`aks-agc-lab-spot`**.
4. Confirm:
   - Node health & utilization meters are active.
   - Pod and namespace inventory is populated.
   - Out-of-the-box alerts and Davis AI anomaly detection are operational.

---

## ⚠️ SRE Production Gotchas & Interview Traps

| Trap | Root Cause | Solution |
| :--- | :--- | :--- |
| **`Secret "dynakube" not found`** | The CSI driver is declarative; it does NOT fetch secrets until a pod mounts the CSI volume. | Deploy the lightweight helper pause pod (`dt-secret-sync-helper`) to trigger the volume mount immediately. |
| **`Permission denied on AKV`** | The AKS Managed Identity does not have the `get` secret permission. | Verify the identity client ID (`addonProfiles.azureKeyvaultSecretsProvider.identity.clientId`) has an active Key Vault Access Policy or `Key Vault Secrets User` RBAC role. |
| **Admission Webhook Timeout** | Webhook pods cannot communicate if network policies or NSGs block port `8443` or `443` from the API server. | Ensure the AKS control plane can reach worker nodes on port `8443` for webhook validation. |
| **Spot Node Eviction** | When running Spot VMs, Azure can evict worker nodes with a 30s notification. | Ensure OneAgent is configured as a DaemonSet with tolerations so it recovers automatically when new spot instances spin up. |

---

## 🧹 Strict Teardown (FinOps Protection)

When you conclude your validation session, run the automated teardown to eliminate ongoing cloud charges:

```bash
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_agc_lab_manager.sh" | bash -s -- down
```
