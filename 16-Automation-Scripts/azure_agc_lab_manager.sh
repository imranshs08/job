#!/bin/bash

# ==============================================================================
# Azure AGC Spot Cluster Manager
# Purpose: Spin up ultra-cheap AKS clusters for Gateway API labs (~$0.01/hr)
#          and securely provision the Application Gateway for Containers (AGC) 
#          ALB Controller, Managed Identities, and Subnets.
# Rules: 
#   1. Always run 'down' immediately after finishing the study session.
#   2. Utilizes 'Standard_B2s' Spot VMs to minimize costs by ~90%.
#   3. Automated end-to-end Gateway API provisioning.
# ==============================================================================

set -euo pipefail

# --- Core Vars ---
RG_NAME="rg-gateway-api-lab"
LOCATION="eastus"
CLUSTER_NAME="aks-agc-lab-spot"
NODE_COUNT="2"
NODE_SIZE="Standard_D2as_v7" 
LOG_FILE="/tmp/azure_agc_lab_$(date +%s).log"

# --- ALB / Gateway Vars ---
ALB_IDENTITY_NAME="azure-alb-identity"
INFRA_NAMESPACE="alb-infra"
ALB_NAME="application-load-balancer"
GATEWAY_NAME="gateway"
GATEWAY_CLASS_NAME="azure-alb-external"

# --- UI Formatting ---
GREEN="\033[1;32m"
BLUE="\033[1;36m"
RED="\033[1;31m"
YELLOW="\033[1;33m"
RESET="\033[0m"

log_info() { echo -e "${BLUE}ℹ️  $1${RESET}"; }
log_step() { echo -ne "${BLUE}>>${RESET} $1... "; }
log_success() { echo -e "${GREEN}✓ [OK]${RESET}"; }
log_fail() { 
    echo -e "${RED}✗ [FAILED]${RESET}"
    echo -e "\n${RED}================= ERROR LOGS =================${RESET}"
    tail -n 25 "$LOG_FILE"
    echo -e "${RED}==============================================${RESET}"
    echo -e "${RED}Check detailed logs at: $LOG_FILE${RESET}"
    exit 1
}

function show_help {
    echo -e "Usage: ./azure_agc_lab_manager.sh [command]"
    echo -e "\nCommands:"
    echo "  up      : Creates RG, AKS, Identity, Subnets, ALB Controller & Gateway CRDs"
    echo "  down    : STRICT TEARDOWN - Deletes the entire Resource Group"
    echo "  status  : Checks if the lab is currently running"
    echo ""
}

if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

COMMAND=$1

case "$COMMAND" in
    up)
        echo -e "${YELLOW}Starting Azure AGC Lab Build. Detailed background logs: ${LOG_FILE}${RESET}"
        touch "$LOG_FILE"

        if az group show --name "$RG_NAME" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Pre-existing lab environment detected! Nuking it to ensure a clean slate...${RESET}"
            log_step "Destroying old Resource Group (Takes ~2-3 mins)"
            az group delete --name "$RG_NAME" --yes >> "$LOG_FILE" 2>&1 || log_fail
            log_success
        fi

        log_step "Registering modern Azure Network Providers"
        {
            az provider register --namespace Microsoft.ContainerService
            az provider register --namespace Microsoft.Network
            az provider register --namespace Microsoft.NetworkFunction
            az provider register --namespace Microsoft.ServiceNetworking
            az extension add --name alb || true
        } >> "$LOG_FILE" 2>&1
        log_success
        
        log_step "Creating resource group ($RG_NAME)"
        az group create --name "$RG_NAME" --location "$LOCATION" >> "$LOG_FILE" 2>&1 || log_fail
        log_success
        
        log_step "Provisioning minimal AKS Cluster (Takes ~3-5 mins)"
        az aks create \
            --resource-group "$RG_NAME" \
            --name "$CLUSTER_NAME" \
            --node-count "$NODE_COUNT" \
            --node-vm-size "$NODE_SIZE" \
            --enable-oidc-issuer \
            --enable-workload-identity \
            --network-plugin azure \
            --generate-ssh-keys >> "$LOG_FILE" 2>&1 || log_fail
        log_success
        
        log_step "Pulling cluster credentials to local Kubeconfig"
        az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing >> "$LOG_FILE" 2>&1 || log_fail
        log_success
        
        if ! command -v helm &> /dev/null; then
            log_step "Installing Helm dependencies"
            curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 -o get_helm.sh
            chmod +x get_helm.sh
            USE_SUDO=false HELM_INSTALL_DIR=/usr/bin ./get_helm.sh >> "$LOG_FILE" 2>&1 || log_fail
            log_success
        fi

        log_step "Querying AKS Infrastructure Resource Group"
        MC_RG=$(az aks show --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --query "nodeResourceGroup" --output tsv 2>>"$LOG_FILE") || log_fail
        MC_RG_ID=$(az group show --name "$MC_RG" --query id --output tsv 2>>"$LOG_FILE") || log_fail
        log_success
        
        log_step "Creating Azure Managed Identity for ALB"
        az identity create --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME" >> "$LOG_FILE" 2>&1 || log_fail
        PRINCIPAL_ID=$(az identity show --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME" --query principalId --output tsv 2>>"$LOG_FILE")
        CLIENT_ID=$(az identity show --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME" --query clientId --output tsv 2>>"$LOG_FILE")
        log_success
        
        log_info "Sleeping 45s for Azure AD Identity replication..."
        sleep 45

        log_step "Assigning Reader Role to Node Resource Group"
        az role assignment create \
            --assignee-object-id "$PRINCIPAL_ID" \
            --assignee-principal-type ServicePrincipal \
            --scope "$MC_RG_ID" \
            --role "Reader" >> "$LOG_FILE" 2>&1 || log_fail
        log_success

        log_step "Configuring Federated Identity for OIDC"
        AKS_OIDC_ISSUER=$(az aks show --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --query "oidcIssuerProfile.issuerUrl" --output tsv 2>>"$LOG_FILE")
        az identity federated-credential create \
            --name "${ALB_IDENTITY_NAME}-federatedIdentity" \
            --identity-name "$ALB_IDENTITY_NAME" \
            --resource-group "$RG_NAME" \
            --issuer "$AKS_OIDC_ISSUER" \
            --subject "system:serviceaccount:${INFRA_NAMESPACE}:alb-controller-sa" >> "$LOG_FILE" 2>&1 || log_fail
        log_success

        log_step "Installing ALB Controller via Helm"
        helm install alb-controller oci://mcr.microsoft.com/application-lb/charts/alb-controller \
            --namespace "$INFRA_NAMESPACE" \
            --create-namespace \
            --version 1.7.9 \
            --skip-schema-validation \
            --set albController.namespace="$INFRA_NAMESPACE" \
            --set albController.podIdentity.clientID="$CLIENT_ID" >> "$LOG_FILE" 2>&1 || log_fail
        log_success
            
        log_step "Deploying Dedicated ALB Subnet"
        AKS_SUBNET_ID=$(az vmss list --resource-group "$MC_RG" --query '[0].virtualMachineProfile.networkProfile.networkInterfaceConfigurations[0].ipConfigurations[0].subnet.id' --output tsv 2>>"$LOG_FILE")
        AKS_VNET_NAME=$(echo "$AKS_SUBNET_ID" | awk -F'/' '{print $9}')
        AKS_VNET_RG=$(echo "$AKS_SUBNET_ID" | awk -F'/' '{print $5}')
        ALB_SUBNET_NAME="alb-subnet"
        SUBNET_ADDRESS_PREFIX="10.225.0.0/24"

        az network vnet subnet create \
            --resource-group "$AKS_VNET_RG" \
            --vnet-name "$AKS_VNET_NAME" \
            --name "$ALB_SUBNET_NAME" \
            --address-prefixes "$SUBNET_ADDRESS_PREFIX" \
            --delegations 'Microsoft.ServiceNetworking/trafficControllers' >> "$LOG_FILE" 2>&1 || log_fail

        ALB_SUBNET_ID=$(az network vnet subnet show --name "$ALB_SUBNET_NAME" --resource-group "$AKS_VNET_RG" --vnet-name "$AKS_VNET_NAME" --query id --output tsv 2>>"$LOG_FILE")
        log_success

        log_step "Assigning Subnet Network RBAC permissions"
        az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --scope "$MC_RG_ID" --role "AppGw for Containers Configuration Manager" >> "$LOG_FILE" 2>&1 || log_fail
        az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal --scope "$ALB_SUBNET_ID" --role "Network Contributor" >> "$LOG_FILE" 2>&1 || log_fail
        log_success

        log_step "Deploying ApplicationLoadBalancer CRD"
cat <<CRD | kubectl apply -f - >> "$LOG_FILE" 2>&1 || log_fail
apiVersion: alb.networking.azure.io/v1
kind: ApplicationLoadBalancer
metadata:
  name: $ALB_NAME
  namespace: $INFRA_NAMESPACE
spec:
  associations:
  - $ALB_SUBNET_ID
CRD
        log_success
        
        log_info "Sleeping 15s for Azure to acknowledge ALB infrastructure target..."
        sleep 15
        
        log_step "Deploying Gateway Resource API"
cat <<CRD | kubectl apply -f - >> "$LOG_FILE" 2>&1 || log_fail
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: $GATEWAY_NAME
  namespace: $INFRA_NAMESPACE
  annotations:
    alb.networking.azure.io/alb-namespace: $INFRA_NAMESPACE
    alb.networking.azure.io/alb-name: $ALB_NAME
spec:
  gatewayClassName: $GATEWAY_CLASS_NAME
  listeners:
  - name: http-listener
    port: 80
    protocol: HTTP
    allowedRoutes:
      namespaces:
        from: All
CRD
        log_success
        
        echo -e "\n${GREEN}========================================================================${RESET}"
        echo -e "${GREEN}✅ LAB STOOD UP SUCCESSFULLY!${RESET}"
        echo -e "${GREEN}========================================================================${RESET}"
        echo "The Application Gateway takes about 5-6 mins to fully terminate and assign an IP."
        echo "Run the following command to check its status:"
        echo -e "   ${BLUE}kubectl get applicationloadbalancer $ALB_NAME -n $INFRA_NAMESPACE -o yaml${RESET}"
        echo ""
        echo "To grab the Gateway Public IP once it is assigned:"
        echo -e "   ${BLUE}kubectl get gateway $GATEWAY_NAME -n $INFRA_NAMESPACE -o jsonpath='{.status.addresses[0].value}'${RESET}"
        echo ""
        echo -e "${YELLOW}⚠️  CRITICAL COST REMINDER: Run './azure_agc_lab_manager.sh down' when done.${RESET}\n"
        ;;
        
    down)
        echo -e "${RED}🛑 NUKING RESOURCE GROUP: $RG_NAME...${RESET}"
        echo "This will destroy the AKS cluster and ALL associated resources (IPs, LBs, Disks)."
        
        if ! az group show --name "$RG_NAME" &>/dev/null; then
            echo -e "\n${GREEN}✅ Resource group '$RG_NAME' is already gone! No action needed.${RESET}"
            exit 0
        fi

        # Issue the delete command
        az group delete --name "$RG_NAME" --yes --no-wait
        
        echo -e "\n${YELLOW}Monitoring destruction progress... (You can press Ctrl+C to exit securely; deletion will continue safely in the background)${RESET}\n"
        
        while az group show --name "$RG_NAME" &>/dev/null; do
            COUNT=$(az resource list --resource-group "$RG_NAME" --query "length(@)" -o tsv 2>/dev/null || echo "0")
            if [ -z "$COUNT" ]; then COUNT="0"; fi
            echo -ne "\r${BLUE}⏳ Resources alive: ${COUNT} ... sweeping Azure backend...${RESET}\033[K"
            sleep 10
        done
        
        echo -e "\n\n${GREEN}✅ TEARDOWN COMPLETE!${RESET}"
        echo "Azure has permanently wiped the environment. Billing has been safely stopped."
        ;;
        
    status)
        echo "🔍 Checking lab resource group status..."
        if az group show --name "$RG_NAME" -o table 2>/dev/null; then
            echo -e "\n${YELLOW}⚠️  LAB IS CURRENTLY RUNNING!${RESET}"
        else
            echo -e "\n${GREEN}✅ LAB IS DOWN (No resource group found).${RESET}"
        fi
        ;;
        
    *)
        echo "❌ Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
