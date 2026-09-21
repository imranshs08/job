#!/bin/bash

# ==============================================================================
# Azure AGC Spot Cluster Manager
# Purpose: Spin up ultra-cheap AKS clusters for Gateway API labs (~$0.01/hr)
# Rules: 
#   1. Always run 'down' immediately after finishing the study session.
#   2. Utilizes 'Standard_B2s' Spot VMs to minimize costs by ~90%.
#   3. Includes required OIDC & Workload Identity for AGC setups.
# ==============================================================================

set -euo pipefail

RG_NAME="rg-gateway-api-lab"
LOCATION="eastus"
CLUSTER_NAME="aks-agc-lab-spot"
NODE_SIZE="Standard_B2s" 

function show_help {
    echo -e "Usage: ./azure_agc_lab_manager.sh [command]"
    echo -e "\nCommands:"
    echo "  up      : Creates the Resource Group and ultra-cheap Spot AKS cluster"
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
        echo "🚀 [1/3] Creating Resource Group: $RG_NAME natively in $LOCATION..."
        az group create --name "$RG_NAME" --location "$LOCATION" -o table
        
        echo "⏳ [2/3] Provisioning AKS Cluster with Spot Instances (this takes ~3-5 mins)..."
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
            
        echo "🔑 [3/3] Pulling cluster credentials into local Kubeconfig..."
        az aks get-credentials --resource-group "$RG_NAME" --name "$CLUSTER_NAME" --overwrite-existing
        
        echo -e "\n✅ LAB STOOD UP SUCCESSFULLY!"
        echo -e "⚠️  CRITICAL COST REMINDER: Run './azure_agc_lab_manager.sh down' when done."
        ;;
        
    down)
        echo "🛑 [1/1] NUKING RESOURCE GROUP: $RG_NAME..."
        echo "This will destroy the AKS cluster and ALL associated resources (IPs, LBs, Disks)."
        
        az group delete --name "$RG_NAME" --yes --no-wait
        
        echo -e "\n✅ Teardown initiated in the background!"
        echo "Azure is safely wiping everything. Billing has been effectively stopped."
        ;;
        
    status)
        echo "🔍 Checking lab resource group status..."
        if az group show --name "$RG_NAME" -o table 2>/dev/null; then
            echo -e "\n⚠️  LAB IS CURRENTLY RUNNING!"
        else
            echo -e "\n✅ LAB IS DOWN (No resource group found)."
        fi
        ;;
        
    *)
        echo "❌ Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
