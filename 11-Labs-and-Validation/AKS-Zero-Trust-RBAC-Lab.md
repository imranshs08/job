# 🔐 SRE Masterclass Lab: The Insider Threat (AKS Zero-Trust)

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

### Step 6 & 7: The Guest Deploys the Workload
To prove they have access, the Guest deploys a standard Nginx application and validates it locally.

```bash
# 6. Deploy Nginx
kubectl create deployment nginx-web --image=nginx
kubectl expose deployment nginx-web --port=80 --type=ClusterIP

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

However, because they previously executed `--admin` to steal the `--local-accounts` certificate, their local kubeconfig **completely bypasses Azure Active Directory**. 

The terminated Guest (`imranshs08`) opens their terminal and strikes the cluster:
```powershell
# Guest acts maliciously
kubectl delete deployment nginx-web
```
**💥 Result:** `deployment.apps "nginx-web" deleted.` 
Even though they were fired from Azure, the static Kubeconfig certificate allowed them to murder the production workload!

---

## 🎬 Act IV: The Zero-Trust Remediation

### Step 10: The Architect Seals the Breach
The Architect realizes they left the Kubernetes API Server exposed to static Local Accounts. They must immediately run the explicit remediation command to disable the backdoor vector.

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
