# 🔐 SRE Masterclass Sandbox: The Insider Threat (AKS Zero-Trust)

This lab is a cinematic, end-to-end execution guide demonstrating a classic "Insider Threat" scenario. We will simulate two engineers: a Senior Admin (`jamiaxpress@gmail.com`) and an invited engineer (`imranshs08@gmail.com`). We will prove mathematically why AKS Local Accounts represent a critical backdoor, and how to permanently board it up using Zero-Trust Architecture.

---

## 🎭 The Cast of Characters
* **The Architect (Admin):** `jamiaxpress@gmail.com`
* **The Guest Engineer (Actor):** `imranshs08@gmail.com`
* **The Target Workload:** A simple `nginx` deployment.

---

## 🎬 Act I: Provisioning & Onboarding

### Step 1 & 2: The Architect Deploys the Cluster (With The Backdoor)
Log into your local CLI as **`jamiaxpress@gmail.com`**. We will deploy a standard AKS cluster. By default, this enables Azure RBAC *and* inherently leaves the Local Accounts (static certificates) wide open.

> **Enterprise DO:** Always explicitly declare `--disable-local-accounts` during provisioning for production clusters.
> **Enterprise DON'T:** Never assume Entra ID integration automatically secures the API Server. It fundamentally does not.

```bash
# Define Constants
RG_NAME="rg-gateway-api-lab"
LOCATION="centralus"
CLUSTER_NAME="aks-agc-lab-spot"

# 1. Spin up the Resource Group
az group create --name "$RG_NAME" --location "$LOCATION"

# 2. Provision the Cluster (Local Accounts Enabled)
az aks create     --resource-group "$RG_NAME"     --name "$CLUSTER_NAME"     --node-count 1     --generate-ssh-keys     --network-plugin azure     --enable-managed-identity     --enable-aad     --enable-azure-rbac
```

### Step 3 & 4: Inviting & Granting Permission to the Guest
The Architect (`jamiaxpress`) now invites the Guest (`imranshs08`) to help manage the cluster.

> **Enterprise DO:** Assign permissions strictly via Entra ID Security Groups, rather than individual direct user mapping.
> **Enterprise DON'T:** Do not grant 'Cluster Admin' for trivial tasks; utilize granular Azure RBAC namespaces.

```bash
# 3. Get the Object ID of the Guest User (imranshs08)
GUEST_EMAIL="imranshs08@gmail.com"
GUEST_ID=$(az ad user show --id $GUEST_EMAIL --query id -o tsv)

# 4. Grant the Guest 'Azure Kubernetes Service RBAC Cluster Admin' rights
SUB_ID=$(az account show --query id -o tsv)
az role assignment create   --role "Azure Kubernetes Service RBAC Cluster Admin"   --assignee $GUEST_ID   --scope /subscriptions/$SUB_ID/resourceGroups/$RG_NAME/providers/Microsoft.ContainerService/managedClusters/$CLUSTER_NAME
```

---

## 🎬 Act II: The Sabotage Setup

### Step 5: The Guest Connects Locally (The Heist)
The Guest (`imranshs08`) signs into Azure CLI on their own laptop. Because they want to ensure they never lose access, they intentionally use the `--admin` flag to pull the raw, static RSA certificate instead of the Entra ID token!

```bash
# Guest executes this on their local PowerShell terminal
az aks get-credentials --resource-group rg-gateway-api-lab --name aks-agc-lab-spot --admin

# Verify the compromised context
kubectl config current-context 
# Output will be: aks-agc-lab-spot-admin (They now hold the static God-Key!)
```

---

## 🧠 SRE Deep-Dive: The Anatomy of a Kubeconfig
Before the Guest attacks, let's understand exactly *what* they just stole. 

**Where is it stored?**
By default, Kubernetes stores this file at `~/.kube/config` on Linux/Mac, or `C:\Users\<YourName>\.kube\config` on Windows. We explicitly saved ours to `insecure-kubeconfig` in the current directory using the `--file` flag.

**The Format:**
A `kubeconfig` is a raw YAML file consisting of three primary pillars:
1. **Clusters:** The API Server URL and the Certificate Authority (CA) data to verify the server is legitimate.
2. **Users:** The authentication payload. This can be an Entra ID token, or (in this deadly scenario) raw RSA `client-certificate-data` and `client-key-data`.
3. **Contexts:** The glue that binds a specific User to a specific Cluster.

**Example of the Stolen Payload:**
```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1... (Base64 CA)
    server: https://aks-agc-la-rg-...hcp.centralus.azmk8s.io:443
  name: aks-agc-lab-spot
contexts:
- context:
    cluster: aks-agc-lab-spot
    user: clusterAdmin_rg-gateway-api-lab_aks-agc-lab-spot
  name: aks-agc-lab-spot-admin
current-context: aks-agc-lab-spot-admin
kind: Config
users:
- name: clusterAdmin_rg-gateway-api-lab_aks-agc-lab-spot
  user:
    client-certificate-data: LS0tLS1C... (Base64 RSA Public Cert)
    client-key-data: LS0tLS1C... (Base64 RSA PRIVATE KEY - The God Key)
```

> **Enterprise Threat Vector (Copy/Paste Execution):** 
> *Can the Guest copy this file and email it to a hacker?* 
> **YES.** Because this specific kubeconfig utilizes static `client-certificate-data` (Local Accounts), it is completely decoupled from Azure Active Directory. The Guest can copy this exact `.yaml` file to *any* computer, smartphone, or CI/CD pipeline on earth, set `export KUBECONFIG=insecure-kubeconfig`, and wield cluster-admin privileges instantly. No MFA, no passwords, no Azure validation required. This is why Local Accounts are so dangerous!

---

### Step 6 & 7: The Guest Deploys the Workload
To prove they have access, the Guest deploys a standard Nginx application using declarative YAML and validates it locally.

**Create `nginx-deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-web
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-web
  namespace: default
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

```bash
# 6. Deploy Nginx
kubectl apply -f nginx-deployment.yaml

# 7. Validate via Port-Forward
kubectl port-forward svc/nginx-web 8080:80
# (Guest can navigate to http://localhost:8080 successfully)
```

---

## 🎬 Act III: Termination & The Insider Strike

### Step 8: The Architect Revokes Access
The Architect (`jamiaxpress`) discovers `imranshs08` has been reckless and decides to terminate their access entirely from the Azure Portal.

```bash
# The Architect revokes the Azure RBAC assignment
az role assignment delete   --role "Azure Kubernetes Service RBAC Cluster Admin"   --assignee $GUEST_ID   --scope /subscriptions/$SUB_ID/resourceGroups/$RG_NAME/providers/Microsoft.ContainerService/managedClusters/$CLUSTER_NAME
```

### Step 9: The Malicious Sabotage
In a perfectly locked-down Zero-Trust environment, `imranshs08` should be instantly locked out. 

However, because they previously executed `--admin` to steal the `--local-accounts` certificate (which is valid for 730 days!), their local kubeconfig **completely bypasses Azure Active Directory**. 

The terminated Guest (`imranshs08`) opens their terminal and strikes the cluster:
```powershell
# Guest acts maliciously
kubectl delete -f nginx-deployment.yaml
```
**💥 Result:** `deployment.apps "nginx-web" deleted.` 
Even though they were fired from Azure, the static Kubeconfig certificate allowed them to murder the production workload!

---

## 🎬 Act IV: The Zero-Trust Remediation

### Step 10: The Architect Seals the Breach
The Architect realizes they left the Kubernetes API Server exposed to static Local Accounts. They must immediately run the explicit remediation command to disable the backdoor vector.

> **Enterprise Warning (Blast Radius):** Running this command will break any Jenkins or GitHub Actions pipelines still utilizing the `--admin` local kubeconfig format. They must be migrated to Azure Service Principals via `kubelogin`.

```bash
# The Architect disables local accounts universally
az aks update   --resource-group rg-gateway-api-lab   --name aks-agc-lab-spot   --disable-local-accounts
```

### Step 11: The Re-Validation (Bad Actor Defeated)
The malicious Guest (`imranshs08`) attempts to launch a second attack using their stolen local `kubeconfig` file.

```powershell
# Guest attempts to attack again
kubectl get pods
```

**🛡️ Expected Output:** 
```text
error: You must be logged in to the server (Unauthorized)
```
**Victory!** 🎯 The API Server completely rejected the static X.509 certificate. The only way to authenticate now is via an active, validated Entra ID token, neutralizing the Insider Threat completely.

---

## 💥 Phase 5: Environment Cleanup (Cost Containment)
To prevent unexpected Azure billing, execute the following teardown logic.

```bash
az group delete --name "rg-gateway-api-lab" --yes --no-wait
```
*Lab executed, compromised, secured, and safely destroyed! 🚀*
