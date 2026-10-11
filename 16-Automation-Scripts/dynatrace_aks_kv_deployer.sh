#!/bin/bash
# ==============================================================================
# SCRIPT: dynatrace_aks_kv_deployer.sh
# PURPOSE: Zero-Trust Dynatrace Observability Platform Deployer on Azure AKS
#
# ARCHITECTURAL HIGHLIGHTS:
# 1. Zero-Trust Secrets Management:
#    - Sensitive Dynatrace tokens (API & Data Ingest) are NEVER hardcoded in YAML.
#    - Tokens are securely pushed to Azure Key Vault (AKV).
#    - AKS Secrets Store CSI Driver syncs them dynamically into a native K8s Secret
#      ('dynakube') using an Azure Managed Identity (Least Privilege).
#
# 2. Cloud-Native Observability:
#    - Deploys the latest stable Dynatrace Operator (v1.11.0) using official YAML.
#    - Utilizes the newest DynaKube Custom Resource API (dynatrace.com/v1beta6).
#    - Configures Cloud-Native Full-Stack OneAgent code injection and ActiveGate
#      Kubernetes API routing.
#
# TARGET ENVIRONMENT:
#    Tenant UI:      https://ybl31832.apps.dynatrace.com/ui
#    Tenant API:     https://ybl31832.apps.dynatrace.com/api/v1
#    AKS Cluster:    aks-agc-lab-spot (in resource group rg-gateway-api-lab)
# ==============================================================================

# Defensive Bash Shell Execution Options:
# -e: Exit immediately if any command exits with a non-zero status.
# -u: Treat unset variables and parameters as an error when performing expansion.
# -o pipefail: Pipeline return status is the value of the last (rightmost) command
#              to exit with a non-zero status.
set -euo pipefail

# ------------------------------------------------------------------------------
# 1. Configuration & Default Environment Variables
# ------------------------------------------------------------------------------
# Resource Group and Cluster names matching azure_agc_lab_manager.sh
RG_NAME="${RG_NAME:-rg-gateway-api-lab}"
CLUSTER_NAME="${CLUSTER_NAME:-aks-agc-lab-spot}"
LOCATION="${LOCATION:-centralus}"

# Dynatrace SaaS Endpoint (Target environment)
DT_API_URL="${DT_API_URL:-https://ybl31832.apps.dynatrace.com/api/v1}"

# Azure Key Vault naming: Appends a random 4-digit number to guarantee globally unique name
KV_NAME="${KV_NAME:-kv-dt-lab-$RANDOM}"

# ------------------------------------------------------------------------------
# 2. Terminal UI Formatting Helpers
# ------------------------------------------------------------------------------
GREEN="\033[1;32m"
BLUE="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

log_info()    { echo -e "${BLUE}ℹ️  $1${RESET}"; }
log_step()    { echo -ne "${BLUE}>>${RESET} $1... "; }
log_success() { echo -e "${GREEN}✓ [OK]${RESET}"; }
log_fail()    { echo -e "${RED}✗ [FAILED]${RESET}"; exit 1; }

echo -e "${YELLOW}================================================================${RESET}"
echo -e "${YELLOW}  Dynatrace Operator & Key Vault CSI Integration for AKS        ${RESET}"
echo -e "${YELLOW}================================================================${RESET}"

# ------------------------------------------------------------------------------
# 3. Input Validation (Ensure Security Tokens are Present in Shell Environment)
# ------------------------------------------------------------------------------
# DT_API_TOKEN is mandatory. If absent, instruct the engineer on required usage.
if [ -z "${DT_API_TOKEN:-}" ]; then
  echo -e "${RED}Error: Environment variable DT_API_TOKEN is not set.${RESET}"
  echo "Usage:"
  echo "  export DT_API_TOKEN=\"dt0c01.SAMPLE...\""
  echo "  export DT_DATA_INGEST_TOKEN=\"dt0c01.SAMPLE...\" # Optional (defaults to DT_API_TOKEN)"
  echo "  ./dynatrace_aks_kv_deployer.sh"
  exit 1
fi

# Fallback: if data ingest token is not separately provided, reuse API token
DT_DATA_INGEST_TOKEN="${DT_DATA_INGEST_TOKEN:-$DT_API_TOKEN}"

# ------------------------------------------------------------------------------
# 4. Authenticate & Connect to Target AKS Cluster
# ------------------------------------------------------------------------------
log_step "Fetching AKS credentials and merging into local kubeconfig"
az aks get-credentials \
  --resource-group "$RG_NAME" \
  --name "$CLUSTER_NAME" \
  --overwrite-existing > /dev/null 2>&1 || log_fail
log_success

# ------------------------------------------------------------------------------
# 5. Provision Azure Key Vault & Store Sensitive Credentials
# ------------------------------------------------------------------------------
log_step "Ensuring Azure Key Vault ($KV_NAME) exists in $RG_NAME"
# Use Access Policies (enable-rbac-authorization false) for lightweight lab isolation
if ! az keyvault show --name "$KV_NAME" --resource-group "$RG_NAME" > /dev/null 2>&1; then
  az keyvault create \
    --name "$KV_NAME" \
    --resource-group "$RG_NAME" \
    --location "$LOCATION" \
    --enable-rbac-authorization false > /dev/null 2>&1 || log_fail
fi
log_success

log_step "Ingesting Dynatrace secrets into Azure Key Vault"
# Secret 1: API Token (Used by Operator to download OneAgent & register cluster with SaaS)
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-api-token" \
  --value "$DT_API_TOKEN" > /dev/null 2>&1 || log_fail

# Secret 2: Data Ingest Token (Used for custom metrics ingestion pipeline)
az keyvault secret set \
  --vault-name "$KV_NAME" \
  --name "dynatrace-data-ingest-token" \
  --value "$DT_DATA_INGEST_TOKEN" > /dev/null 2>&1 || log_fail
log_success

# ------------------------------------------------------------------------------
# 6. Enable AKS Secrets Store CSI Driver Add-On
# ------------------------------------------------------------------------------
log_step "Enabling Azure Key Vault Secrets Provider Add-on on AKS"
# This provisions the DaemonSet 'secrets-store-csi-driver' and managed identity in AKS
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name "$CLUSTER_NAME" \
  --resource-group "$RG_NAME" > /dev/null 2>&1 || log_fail
log_success

# ------------------------------------------------------------------------------
# 7. Bind Managed Identity with Key Vault Secret Permissions
# ------------------------------------------------------------------------------
log_step "Configuring Key Vault Access Policy for CSI Managed Identity"
# Harvest the auto-generated User-Assigned Managed Identity client ID
CSI_IDENTITY_CLIENT_ID=$(az aks show \
  --resource-group "$RG_NAME" \
  --name "$CLUSTER_NAME" \
  --query "addonProfiles.azureKeyvaultSecretsProvider.identity.clientId" \
  -o tsv)

# Grant 'get' and 'list' permissions so the driver can retrieve the tokens
az keyvault set-policy \
  --name "$KV_NAME" \
  --secret-permissions get list \
  --spn "$CSI_IDENTITY_CLIENT_ID" > /dev/null 2>&1 || log_fail

# Extract Azure AD Tenant ID
AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)
log_success

# ------------------------------------------------------------------------------
# 8. Create Dynatrace Namespace & Deploy SecretProviderClass
# ------------------------------------------------------------------------------
log_step "Ensuring 'dynatrace' namespace exists"
kubectl create namespace dynatrace --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1 || log_fail
log_success

log_step "Applying SecretProviderClass (mapping Key Vault to K8s Secret 'dynakube')"
# CRITICAL SRE NOTE: The DynaKube CR strictly expects a Kubernetes Secret named 'dynakube'
# containing the keys 'apiToken' and 'dataIngestToken'.
# The 'secretObjects' stanza instructs the CSI driver to create and synchronize this secret!
cat <<EOF | kubectl apply -f - > /dev/null 2>&1 || log_fail
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
log_success

# ------------------------------------------------------------------------------
# 9. Trigger CSI Volume Mount to Materialize the Kubernetes Secret
# ------------------------------------------------------------------------------
log_step "Deploying CSI Secret Sync Pod to trigger Kubernetes Secret creation"
# GOTCHA: The Secrets Store CSI driver does NOT create Kubernetes Secrets on apply;
# it only materializes secrets when a pod mounts the CSI volume.
# We deploy a lightweight pause container to execute this mount immediately.
cat <<EOF | kubectl apply -f - > /dev/null 2>&1 || log_fail
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
log_success

# ------------------------------------------------------------------------------
# 10. Deploy Dynatrace Operator via Official Release YAML Manifests (v1.11.0)
# ------------------------------------------------------------------------------
log_step "Deploying Dynatrace Operator v1.11.0 YAML Manifest (with CSI support)"
# Using official GitHub release manifest containing CRDs, RBAC, and Operator Deployment
kubectl apply -f https://github.com/Dynatrace/dynatrace-operator/releases/download/v1.11.0/kubernetes-csi.yaml > /dev/null 2>&1 || log_fail

# Block until the operator deployment is healthy and ready to process Custom Resources
log_step "Waiting for Dynatrace Operator Pod readiness"
kubectl wait --namespace dynatrace \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=dynatrace-operator \
  --timeout=300s > /dev/null 2>&1 || log_fail
log_success

# ------------------------------------------------------------------------------
# 11. Deploy DynaKube Custom Resource (Latest API: dynatrace.com/v1beta6)
# ------------------------------------------------------------------------------
log_step "Deploying DynaKube Custom Resource (API: dynatrace.com/v1beta6)"
# DynaKube configuration breakdown:
# - apiUrl: Points to Dynatrace SaaS environment.
# - tokens: Points to the K8s Secret 'dynakube' created by CSI.
# - cloudNativeFullStack: Provides automatic container injection + host monitoring.
# - activeGate: Deploys containerized ActiveGate for routing & K8s cluster API monitoring.
cat <<EOF | kubectl apply -f - > /dev/null 2>&1 || log_fail
apiVersion: dynatrace.com/v1beta6
kind: DynaKube
metadata:
  name: dynakube
  namespace: dynatrace
  annotations:
    feature.dynatrace.com/csi-daemonset: "true"
spec:
  apiUrl: "$DT_API_URL"
  tokens: "dynakube"
  oneAgent:
    cloudNativeFullStack: {}
  activeGate:
    capabilities:
      - routing
      - kubernetes-monitoring
EOF
log_success

# ------------------------------------------------------------------------------
# 12. Completion & Verification Instructions
# ------------------------------------------------------------------------------
echo -e "\n${GREEN}================================================================${RESET}"
echo -e "${GREEN}✅ Dynatrace Operator & DynaKube v1beta6 Deployed Successfully! ${RESET}"
echo -e "${GREEN}================================================================${RESET}"
echo -e "Target Tenant: ${BLUE}https://ybl31832.apps.dynatrace.com/ui${RESET}"
echo ""
echo "Verify status with the following diagnostic commands:"
echo -e "  1. Check DynaKube CR:    ${BLUE}kubectl get dynakube -n dynatrace${RESET}"
echo -e "  2. Check Operator Pods:   ${BLUE}kubectl get pods -n dynatrace -o wide${RESET}"
echo -e "  3. Check OneAgent Daemon: ${BLUE}kubectl get daemonset -n dynatrace${RESET}"
echo -e "  4. Check Synced Secret:   ${BLUE}kubectl get secret dynakube -n dynatrace -o yaml${RESET}"
echo ""
echo -e "${YELLOW}⚠️  COST WARNING: Remember to run 'azure_agc_lab_manager.sh down' when finished.${RESET}\n"
