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
NODE_SIZE="Standard_B2s" 

# --- ALB / Gateway Vars ---
ALB_IDENTITY_NAME="azure-alb-identity" # Name required by Azure
INFRA_NAMESPACE="alb-infra"
ALB_NAME="application-load-balancer"
GATEWAY_NAME="gateway"
GATEWAY_CLASS_NAME="azure-alb-external"

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
        # 1. Register Providers
        echo "🔧 [1/10] Registering Required Azure Providers & Extensions..."
        az provider register --namespace Microsoft.ContainerService
        az provider register --namespace Microsoft.Network
        az provider register --namespace Microsoft.NetworkFunction
        az provider register --namespace Microsoft.ServiceNetworking
        az extension add --name alb 2>/dev/null || true

        # 2. Resource Group & AKS
        echo "🚀 [2/10] Creating Resource Group: $RG_NAME in $LOCATION..."
        az group create --name "$RG_NAME" --location "$LOCATION" -o table
        
        echo "⏳ [3/10] Provisioning AKS Cluster with Spot Instances (this takes ~3-5 mins)..."
        az aks create \
            --resource-group "$RG_NAME" \
            --name "$CLUSTER_NAME" \
            --node-count 1 \
            --node-vm-size "$NODE_SIZE" \
            --enable-spot-node-pool \
            --priority Spot \
            --enable-oidc-issuer \
            --enable-workload-identity \
            --network-plugin azure \
            --generate-ssh-keys \
            --out table
            
        echo "🔑 [4/10] Pulling cluster credentials into local Kubeconfig..."
        az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing
        
        # 3. Helm Installation Check
        if ! command -v helm &> /dev/null; then
            echo "🔧 Installing Helm..."
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        fi

        # 4. Identity & RBAC
        echo "🔐 [5/10] Configuring Managed Identity & RBAC for ALB..."
        MC_RG=$(az aks show --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --query "nodeResourceGroup" --output tsv)
        MC_RG_ID=$(az group show --name "$MC_RG" --query id --output tsv)

        az identity create --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME"
        PRINCIPAL_ID=$(az identity show --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME" --query principalId --output tsv)
        CLIENT_ID=$(az identity show --resource-group "$RG_NAME" --name "$ALB_IDENTITY_NAME" --query clientId --output tsv)
        
        echo "  -> Waiting 45s for identity replication across Microsoft Entra..."
        sleep 45

        az role assignment create \
            --assignee-object-id "$PRINCIPAL_ID" \
            --assignee-principal-type ServicePrincipal \
            --scope "$MC_RG_ID" \
            --role "Reader"

        AKS_OIDC_ISSUER=$(az aks show --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --query "oidcIssuerProfile.issuerUrl" --output tsv)
        az identity federated-credential create \
            --name "${ALB_IDENTITY_NAME}-federatedIdentity" \
            --identity-name "$ALB_IDENTITY_NAME" \
            --resource-group "$RG_NAME" \
            --issuer "$AKS_OIDC_ISSUER" \
            --subject "system:serviceaccount:${INFRA_NAMESPACE}:alb-controller-sa"

        # 5. Install ALB Controller
        echo "📦 [6/10] Installing ALB Controller via Helm..."
        helm install alb-controller oci://mcr.microsoft.com/application-lb/charts/alb-controller \
            --namespace "$INFRA_NAMESPACE" \
            --create-namespace \
            --version 1.7.9 \
            --skip-schema-validation \
            --set albController.namespace="$INFRA_NAMESPACE" \
            --set albController.podIdentity.clientID="$CLIENT_ID"
            
        # 6. Target the VNET and Subnet
        echo "🌐 [7/10] Creating Delegated Subnet for ALB..."
        AKS_SUBNET_ID=$(az vmss list --resource-group "$MC_RG" --query '[0].virtualMachineProfile.networkProfile.networkInterfaceConfigurations[0].ipConfigurations[0].subnet.id' --output tsv)
        AKS_VNET_NAME=$(echo "$AKS_SUBNET_ID" | awk -F'/' '{print $9}')
        AKS_VNET_RG=$(echo "$AKS_SUBNET_ID" | awk -F'/' '{print $5}')
        
        ALB_SUBNET_NAME="alb-subnet"
        SUBNET_ADDRESS_PREFIX="10.225.0.0/24"

        az network vnet subnet create \
            --resource-group "$AKS_VNET_RG" \
            --vnet-name "$AKS_VNET_NAME" \
            --name "$ALB_SUBNET_NAME" \
            --address-prefixes "$SUBNET_ADDRESS_PREFIX" \
            --delegations 'Microsoft.ServiceNetworking/trafficControllers'

        ALB_SUBNET_ID=$(az network vnet subnet show --name "$ALB_SUBNET_NAME" --resource-group "$AKS_VNET_RG" --vnet-name "$AKS_VNET_NAME" --query id --output tsv)

        echo "  -> Applying Network RBAC for ALB..."
        az role assignment create \
            --assignee-object-id "$PRINCIPAL_ID" \
            --assignee-principal-type ServicePrincipal \
            --scope "$MC_RG_ID" \
            --role "AppGw for Containers Configuration Manager" 

        az role assignment create \
            --assignee-object-id "$PRINCIPAL_ID" \
            --assignee-principal-type ServicePrincipal \
            --scope "$ALB_SUBNET_ID" \
            --role "Network Contributor" 

        # 7. Apply CRDs
        echo "🚢 [8/10] Creating ApplicationLoadBalancer CRD..."
cat <<CRD | kubectl apply -f -
apiVersion: alb.networking.azure.io/v1
kind: ApplicationLoadBalancer
metadata:
  name: $ALB_NAME
  namespace: $INFRA_NAMESPACE
spec:
  associations:
  - $ALB_SUBNET_ID
CRD
        
        echo "  -> Sleeping for 15s to allow Azure to acknowledge ALB resource..."
        sleep 15
        
        echo "🔮 [9/10] Creating Gateway Resource..."
cat <<CRD | kubectl apply -f -
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
        
        echo -e "\n✅ [10/10] LAB STOOD UP SUCCESSFULLY!"
        echo "The Application Gateway takes about 5-6 mins to fully terminate and assign an IP."
        echo "Run the following command to check its status:"
        echo -e "\033[1;36mkubectl get applicationloadbalancer $ALB_NAME -n $INFRA_NAMESPACE -o yaml \033[0m"
        echo ""
        echo "To grab the Gateway IP once it is assigned:"
        echo -e "\033[1;36mkubectl get gateway $GATEWAY_NAME -n $INFRA_NAMESPACE -o jsonpath='{.status.addresses[0].value}'\033[0m"
        echo ""
        echo -e "⚠️  CRITICAL COST REMINDER: Run './azure_agc_lab_manager.sh down' when done."
        ;;
        
    down)
        echo "🛑 [1/1] NUKING RESOURCE GROUP: $RG_NAME..."
        echo "This will destroy the AKS c
