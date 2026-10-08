# 🔐 SRE Masterclass Lab: AKS Zero-Trust RBAC & Identity Isolation

This lab is a comprehensive, end-to-end execution guide designed to validate Microsoft Entra ID (Azure AD) integration with Azure Kubernetes Service (AKS). It explicitly demonstrates the "Local Account Zero-Day Vulnerability", how to remediate it, and how to safely leverage OIDC Group Inheritance.

---

## 🎯 Lab Objectives
1. **Context Manipulation:** Master `kubeconfig` and `kubectl config current-context` to switch between privileged Admin certificates and standardized Entra ID tokens.
2. **The Sabotage:** Exploit the `--admin` flag to extract static RSA client certificates.
3. **The Remediation:** Disable local accounts and forcefully map Kubernetes data-plane access to Azure RBAC.
4. **Entra ID Inheritance:** Prove that `Reader` accounts can inherit `Cluster-Admin` backend rights via invisible AAD Security Group memberships.

---

## 🏗️ Prerequisites: Cluster Provisioning
If you do not have a cluster deployed, run the following block to spin up the required native Azure architecture. (These are the exact execution parameters extracted from your background provisioning script):

```bash
RG_NAME="rg-gateway-api-lab"
LOCATION="eastus"
CLUSTER_NAME="aks-agc-lab-spot"

# 1. Spin up the dedicated Resource Group
az group create --name "$RG_NAME" --location "$LOCATION"

# 2. Provision the AKS Cluster (Local Accounts inherently enabled by default)
az aks create     --resource-group "$RG_NAME"     --name "$CLUSTER_NAME"     --node-count 1     --generate-ssh-keys     --network-plugin azure     --enable-managed-identity
```

---

## 🛑 Phase 1: Exposing The Local Account Vulnerability

Wait! Before you begin, ensure your cluster currently has local accounts *enabled* (this is the default behavior on older AKS deployments).

### 1.1 Exploit the Cluster (Extract the Static God-Key)
Run this command to bypass Entra ID entirely and pull the static `clusterUser` certificate:
```bash
az aks get-credentials --resource-group rg-gateway-api-lab --name aks-agc-lab-spot --admin --file insecure-kubeconfig
```

### 1.2 Validate the Cryptographic Payload
Inspect the raw file you just downloaded. Look for `client-certificate-data` and `client-key-data`:
```bash
kubectl config view --kubeconfig insecure-kubeconfig --raw
```
*Notice how there is NO Entra ID token here. This is raw X.509 cryptography.*

### 1.3 Prove Context Independence
Switch your active terminal session to strictly use this compromised file and prove you have God-Mode:
```bash
export KUBECONFIG=insecure-kubeconfig
kubectl config current-context
kubectl get pods -A
```
*Output: You will successfully see all pods. If you gave this file to a stranger, they would have immediate control of the cluster for 2 Full Years.*

---

## 👔 Phase 2: Entra ID Provisioning & Real-World Authorization

Now we will create a dedicated Azure AD Security Group to govern backend access properly.

### 2.1 Create the Entra ID Assets
We will create a specific Azure Group and user for testing:
```bash
# 1. Create a Security Group
az ad group create --display-name "AKS-SRE-Admins" --mail-nickname "akssreadmins"

# 2. Get the Object ID of the Group (SAVE THIS)
GROUP_ID=$(az ad group show --group "AKS-SRE-Admins" --query id -o tsv)

# 3. Extract the Object ID of the Target User dynamically (Save to Variable)
# Replace this exact email with the target user you are testing with
USER_EMAIL="reader@jamiaxpressgmail.onmicrosoft.com"
USER_ID=$(az ad user show --id $USER_EMAIL --query id -o tsv)

# 4. Add the User to the Security Group using the Dynamic Variables
az ad group member add --group "AKS-SRE-Admins" --member-id $USER_ID
```

### 2.2 Wire the Group to Azure RBAC for Kubernetes
Instead of relying on Kubernetes-native `ClusterRoleBindings`, we will grant the entire Group administrative control over the cluster via Azure IAM:
```bash
az role assignment create \
  --role "Azure Kubernetes Service RBAC Cluster Admin" \
  --assignee $GROUP_ID \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-gateway-api-lab/providers/Microsoft.ContainerService/managedClusters/aks-agc-lab-spot
```

---

## 🛡️ Phase 3: The Zero-Trust Remediation

### 3.1 Engage the Prerequisite (Enable Azure AD)
Before we can disable the static backdoor, we must satisfy the Kubernetes v1.25 Lockout Safeguard (otherwise Azure Resource Manager will throw a `BadRequest` error).
```bash
az aks update \
  --resource-group rg-gateway-api-lab \
  --name aks-agc-lab-spot \
  --enable-aad \
  --enable-azure-rbac
```

### 3.2 Terminate the Local Account Backdoor
Destroy the static certificates forever:
```bash
az aks update \
  --resource-group rg-gateway-api-lab \
  --name aks-agc-lab-spot \
  --disable-local-accounts
```

---

## 🧪 Phase 4: SRE Verification & The Inheritance Blindspot

Your cluster is now operating strictly under the **Zero-Trust Model**. Let's prove it mathematically.

### 4.1 Validate the Backdoor is Permanently Boarded Up
Attempt to pull the static credentials again (this time using the normal `~/.kube/config` location):
```bash
unset KUBECONFIG
az aks get-credentials --resource-group rg-gateway-api-lab --name aks-agc-lab-spot --admin
```
**🔥 Expected Output:** 
```text
AuthorizationFailed: Getting static credential is not allowed because this cluster is set to disable local accounts.
```
*Victory! The exploit is permanently disabled.*

### 4.2 Validate Standard Entra ID Login (`kubelogin`)
Now, attempt to log in using the secure OIDC method:
```bash
az aks get-credentials --resource-group rg-gateway-api-lab --name aks-agc-lab-spot --overwrite-existing
kubelogin convert-kubeconfig -l azurecli
```
Verify your context has shifted dynamically:
```bash
kubectl config current-context
kubectl config get-users
```
*Notice your user now lists `kubelogin` logic instead of static RSA keys.*

### 4.3 Validate Group Inheritance (The Blindspot)
Your individual user might only have the `Reader` role assigned to them in the Azure Portal. However, because you injected them into the `AKS-SRE-Admins` group earlier, they will dynamically inherit `kubectl delete` permissions!

```bash
# As the Reader User:
kubectl get pods -n kube-system
kubectl delete pod csi-azuredisk-node-<HASH> -n kube-system
```
**💥 Expected Output:** `pod "csi-azuredisk-node-xxxx" deleted`

### 4.4 The Final Revocation
To instantly kill the user's backend Kubernetes access, simply evict them from the Entra ID Group:
```bash
az ad group member remove --group "AKS-SRE-Admins" --member-id $USER_ID
```
Wait 2 minutes for token expiration, run `kubectl get pods`, and watch them get slammed with a cold, unforgiving **Error from server (Forbidden)**!
