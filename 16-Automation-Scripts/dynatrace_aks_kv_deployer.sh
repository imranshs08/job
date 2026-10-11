#!/bin/bash
# ==============================================================================
# Dynatrace Operator & Azure Key Vault Secrets Integration Deployer for AKS
# Target Tenant: https://ybl31832.apps.dynatrace.com
# ==============================================================================

set -euo pipefail

# Configuration
RG_NAME="${RG_NAME:-rg-gateway-api-lab}"
CLUSTER_NAME="${CLUSTER_NAME:-aks-agc-lab-spot}"
LOCATION="${LOCATION:-centralus}"
DT_API_URL="${DT_API_URL:-https://ybl31832.apps.dynatrace.com/api/v1}"
KV_NAME="${KV_NAME:-kv-dt-lab-$RANDOM}"

# Styling
GREEN="\033[1;32m"
BLUE="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

log_info() { echo -e "${BLUE}ℹ️  $1${RESET}"; }
log_step() { echo -ne "${BLUE}>>${RESET} $1... "; }
log_success() { echo -e "${GREEN}✓ [OK]${RESET}"; }
log_fail() { echo -e "${RED}✗ [FAILED]${RESET}"; exit 1; }

echo -e "${YELLOW}================================================================${RESET}"
echo -e "${YELLOW}  Dynatrace Operator & Key Vault CSI Integration for AKS        ${RESET}"
echo -e "${YELLOW}================================================================${RESET}"

if [ -z "${DT_API_TOKEN:-}" ]; then
  echo -e "${RED}Error: Environment variable DT_API_TOKEN is not set.${RESET}"
  echo "Usage: DT_API_TOKEN=\"dt0c01...\" DT_DATA_INGEST_TOKEN=\"dt0c01...\" ./dynatrace_aks_kv_deployer.sh"
  exit 1
fi

DT_DATA_INGEST_TOKEN="${DT_DATA_INGEST_TOKEN:-$DT_API_TOKEN}"

log_step "Fetching AKS credentials"
az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing > /dev/null 2>&1 || log_fail
log_success

log_step "Ensuring Azure Key Vault ($KV_NAME) exists"
if ! az keyvault show --name "$KV_NAME" --resource-group "$RG_NAME" > /dev/null 2>&1; then
  az keyvault create --name "$KV_NAME" --resource-group "$RG_NAME" --location "$LOCATION" --enable-rbac-authorization false > /dev/null 2>&1 || log_fail
fi
log_success

log_step "Storing Dynatrace tokens in Key Vault"
az keyvault secret set --vault-name "$KV_NAME" --name "dynatrace-api-token" --value "$DT_API_TOKEN" > /dev/null 2>&1 || log_fail
az keyvault secret set --vault-name "$KV_NAME" --name "dynatrace-data-ingest-token" --value "$DT_DATA_INGEST_TOKEN" > /dev/null 2>&1 || log_fail
log_success

log_step "Enabling Secrets Store CSI Driver addon on AKS"
az aks enable-addons --addons azure-keyvault-secrets-provider --name "$CLUSTER_NAME" --resource-group "$RG_NAME" > /dev/null 2>&1 || log_fail
log_success

log_step "Configuring Key Vault permissions for CSI Driver Managed Identity"
CSI_IDENTITY_CLIENT_ID=$(az aks show --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --query "addonProfiles.azureKeyvaultSecretsProvider.identity.clientId" -o tsv)
az keyvault set-policy --name "$KV_NAME" --secret-permissions get list --spn "$CSI_IDENTITY_CLIENT_ID" > /dev/null 2>&1 || log_fail
AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)
log_success

log_step "Creating dynatrace namespace"
kubectl create namespace dynatrace --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1 || log_fail
log_success

log_step "Applying SecretProviderClass (syncing to secret 'dynakube')"
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

log_step "Deploying CSI Secret Sync Pod"
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

log_step "Installing Dynatrace Operator via Official YAML Manifests (v1.11.0)"
kubectl apply -f https://github.com/Dynatrace/dynatrace-operator/releases/download/v1.11.0/kubernetes-csi.yaml > /dev/null 2>&1 || log_fail
kubectl wait --namespace dynatrace --for=condition=ready pod --selector=app.kubernetes.io/name=dynatrace-operator --timeout=300s > /dev/null 2>&1 || log_fail
log_success

log_step "Deploying DynaKube Custom Resource (API: dynatrace.com/v1beta6)"
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

echo -e "\n${GREEN}================================================================${RESET}"
echo -e "${GREEN}✅ Dynatrace Operator & DynaKube Deployed Successfully!         ${RESET}"
echo -e "${GREEN}================================================================${RESET}"
echo "Verify status with:"
echo "  kubectl get dynakube -n dynatrace"
echo "  kubectl get pods -n dynatrace -o wide"
