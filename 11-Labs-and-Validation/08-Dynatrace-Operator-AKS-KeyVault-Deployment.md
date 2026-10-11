# Lab 08: Dynatrace Operator & DynaKube Deployment on AKS via Azure Key Vault CSI Driver

## Executive Architecture Overview
In enterprise Kubernetes environments, storing sensitive observability tokens (PaaS, API tokens, and Data Ingest tokens) in plaintext Kubernetes manifests violates Zero-Trust security principles. This lab documents the deployment of the official **Dynatrace Operator** and **DynaKube Custom Resource** on an AKS cluster built using our Automated Gateway API Lab Manager (`azure_agc_lab_manager.sh`), with secrets securely ingested from **Azure Key Vault** via the **Secrets Store CSI Driver** and synced to the native `dynakube` Kubernetes Secret.

```
                      +------------------------------------------+
                      |         Azure Key Vault (AKV)            |
                      |   - dynatrace-api-token                  |
                      |   - dynatrace-data-ingest-token          |
                      +--------------------+---------------------+
                                           |
                              Azure Managed Identity
                                           |
                      +--------------------v---------------------+
                      |    Secrets Store CSI Driver (AKS)        |
                      |     SecretProviderClass (dynatrace)      |
                      +--------------------+---------------------+
                                           | Sync as K8s Secret
                      +--------------------v---------------------+
                      |        k8s Secret: "dynakube"            |
                      |      Namespace: dynatrace                |
                      +--------------------+---------------------+
                                           |
                      +--------------------v---------------------+
                      |         Dynatrace Operator               |
                      |        DynaKube CR (Full-Stack)          |
                      +--------------------+---------------------+
                                           | Connects via TLS
                      +--------------------v---------------------+
                      | Dynatrace SaaS Tenant                    |
                      | https://ybl31832.apps.dynatrace.com      |
                      +------------------------------------------+
```

---

## 🎯 Lab Objectives
1. Spin up the AKS Spot cluster using the automated Azure AGC lab manager script.
2. Harvest API and Ingestion tokens from the target Dynatrace Tenant (`https://ybl31832.apps.dynatrace.com`).
3. Store tokens in Azure Key Vault and configure Access Policies for the AKS Secrets Store CSI Driver identity.
4. Deploy a `SecretProviderClass` configured to automatically materialize the `dynakube` Secret.
5. Install the **Dynatrace Operator** via Helm.
6. Apply the **DynaKube** Custom Resource for `cloudNativeFullStack` observability.
7. Verify live telemetry, DaemonSets, and host discovery in the Dynatrace console.

---

## Step 1: Provisioning the AKS Infrastructure

Execute the remote automation manager to create the cluster with Workload Identity and OIDC enabled:

```bash
# 1. Spin up the lab cluster (~3-5 mins)
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_agc_lab_manager.sh" | bash -s -- up

# 2. Set environment parameters
export RG_NAME="rg-gateway-api-lab"
export CLUSTER_NAME="aks-agc-lab-spot"
export LOCATION="centralus"
export DT_TENANT_API="https://ybl31832.apps.dynatrace.com/api/v1"
export KV_NAME="kv-dt-lab-$RANDOM"

# 3. Authenticate local kubeconfig context
az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing

# 4. Verify cluster nodes
kubectl get nodes -o wide
```

---

## Step 2: Dynatrace SaaS Token Generation

1. Navigate to **[Dynatrace UI](https://ybl31832.apps.dynatrace.com/ui)**.
2. Go to **Manage** > **Access tokens**.
3. Generate **API Token** (`k8s-operator-token`):
   - Scopes:
     - `InstallerDownload`
     - `DataExport`
     - `ReadConfig`
     - `WriteConfig`
     - `activeGates.read`
     - `activeGates.write`
4. Generate **Data Ingest Token** (`k8s-data-ingest-token`):
   - Scope: `metrics.ingest`

---

## Step 3: Azure Key Vault Configuration & Secret Provisioning

```bash
# 1. Provision Key Vault in the cluster resource group
az keyvault create \
  --name "$KV_NAME" \
  --resource-group "$RG_NAME" \
  --location "$LOCATION" \
  --enable-rbac-authorization false

# 2. Store the API Token
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-api-token" \
  --value "<YOUR_DYNATRACE_API_TOKEN>"

# 3. Store the Data Ingest Token
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-data-ingest-token" \
  --value "<YOUR_DYNATRACE_DATA_INGEST_TOKEN>"
```

---

## Step 4: Secrets Store CSI Driver & K8s Secret Sync Setup

```bash
# 1. Enable Azure Key Vault Secrets Provider addon on AKS
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name "$CLUSTER_NAME" \
  --resource-group "$RG_NAME"

# 2. Harvest CSI Driver Managed Identity Client ID
CSI_IDENTITY_CLIENT_ID=$(az aks show \
  --resource-group "$RG_NAME" \
  --name "$CLUSTER_NAME" \
  --query "addonProfiles.azureKeyvaultSecretsProvider.identity.clientId" \
  -o tsv)

# 3. Grant Secret GET & LIST permissions to the CSI identity
az keyvault set-policy \
  --name "$KV_NAME" \
  --secret-permissions get list \
  --spn "$CSI_IDENTITY_CLIENT_ID"

AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)

# 4. Create dynatrace namespace
kubectl create namespace dynatrace

# 5. Apply SecretProviderClass with auto-sync to secretName 'dynakube'
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

# 6. Materialize the secret using a minimal inline sync pod
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

# 7. Confirm the secret is generated
kubectl get secret dynakube -n dynatrace -o yaml
```

---

## Step 5: Install Dynatrace Operator via Pure YAML Manifests

We apply the official Kubernetes manifest for the latest stable Dynatrace Operator release (`v1.11.0`) with CSI Driver support:

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

## Step 6: Deploy DynaKube Custom Resource (Latest API: `dynatrace.com/v1beta6`)

Apply the `DynaKube` Custom Resource using the latest supported beta API version (`v1beta6`), configured for full cloud-native stack observability:

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
  # Dynatrace SaaS Tenant API endpoint
  apiUrl: "https://ybl31832.apps.dynatrace.com/api/v1"

  # Reference to the K8s Secret populated from Azure Key Vault
  tokens: "dynakube"

  # Cloud-native full-stack monitoring (automated injection + host monitoring)
  oneAgent:
    cloudNativeFullStack: {}

  # Containerized ActiveGate for Kubernetes API monitoring and metric routing
  activeGate:
    capabilities:
      - routing
      - kubernetes-monitoring
EOF
```

---

## Step 7: Verification & Health Checks

```bash
# 1. Check DynaKube status
kubectl get dynakube -n dynatrace

# 2. Verify all OneAgent, ActiveGate, and Operator pods
kubectl get pods -n dynatrace -o wide

# 3. Verify DaemonSet status across nodes
kubectl get daemonset -n dynatrace

# 4. View live logs from Dynatrace Operator
kubectl logs -n dynatrace -l app.kubernetes.io/name=dynatrace-operator --tail=50 -f
```

### Dynatrace UI Verification:
- Go to `https://ybl31832.apps.dynatrace.com/ui`.
- Navigate to **Kubernetes** from the left navigation pane.
- Confirm cluster `aks-agc-lab-spot` displays green status with node and workload metrics streaming.

---

## Step 8: Strict Lab Teardown (FinOps Cost Control)

Once your verification is complete, destroy the entire lab resource group:

```bash
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_agc_lab_manager.sh" | bash -s -- down
```
