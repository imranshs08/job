#!/bin/bash
# Azure Windows Server 2019 Patching Lab - Automated Provisioner
# Author: Antigravity SRE
set -euo pipefail

RG_NAME="rg-win-patch-lab-2027"
LOCATION="eastus"
VM_NAME="vm-win2019-lab"
ADMIN_USER="labadmin"
# Generates a pseudo-random secure password
ADMIN_PASS="AzureLab@2027!$RANDOM"

# Print colored text
print_msg() { echo -e "\n\033[1;36m==>\033[0m \033[1m$1\033[0m"; }

command=${1:-"help"}

if [ "$command" == "up" ]; then
    print_msg "🚀 Provisioning Cost-Optimized Windows 2019 Lab..."
    az group create --name "$RG_NAME" --location "$LOCATION" -o none
    
    print_msg "⚙️ Deploying VM: $VM_NAME (Series: Standard_B2s, Storage: Standard HDD)"
    print_msg "⏳ This usually takes ~3-5 minutes. Please wait..."
    
    az vm create \
        --resource-group "$RG_NAME" \
        --name "$VM_NAME" \
        --image "Win2019Datacenter" \
        --admin-username "$ADMIN_USER" \
        --admin-password "$ADMIN_PASS" \
        --size "Standard_B2s" \
        --storage-sku "Standard_LRS" \
        --nsg-rule "RDP" \
        --public-ip-sku "Basic" \
        --output none
        
    print_msg "🔄 Enforcing 'Manual' patch orchestration for Azure Update Manager..."
    # Disables automatic VM-level updates so Azure Update Manager (Portal) can fully control patching cycles
    az vm update \
        -g "$RG_NAME" \
        -n "$VM_NAME" \
        --set osProfile.windowsConfiguration.enableAutomaticUpdates=false \
        --output none

    IP_ADDRESS=$(az vm show -d -g "$RG_NAME" -n "$VM_NAME" --query publicIps -o tsv)

    echo -e "\n\033[1;32m✅ Lab Provisioned Successfully!\033[0m"
    echo "============================================="
    echo "🖥️ VM Name      : $VM_NAME"
    echo "👤 Username     : $ADMIN_USER"
    echo "🔑 Password     : $ADMIN_PASS"
    echo "🌐 Public IP    : $IP_ADDRESS"
    echo "⚡ Connect      : mstsc /v:$IP_ADDRESS"
    echo "============================================="

elif [ "$command" == "down" ]; then
    print_msg "🗑️ Destroying Lab and all resources..."
    if az group exists --name "$RG_NAME"; then
        az group delete --name "$RG_NAME" --yes --no-wait
        echo -e "\033[1;32m✅ Teardown initiated. Resources will be deleted safely in the background.\033[0m"
    else
        echo -e "\033[1;33m⚠️ Lab resource group '$RG_NAME' does not exist.\033[0m"
    fi
else
    print_msg "❌ Invalid command. Usage: curl -sSL <url> | bash -s -- [up|down]"
fi
