#!/bin/bash
# Azure Windows Server 2019 Patching Lab - Automated Provisioner
# Author: Antigravity SRE
set -euo pipefail

VM_NAME="vm-win2019-lab"
ADMIN_USER="labadmin"
ADMIN_PASS="AzureLab@2027!$RANDOM"

print_msg() { echo -e "\n\033[1;36m==>\033[0m \033[1m$1\033[0m"; }

command=${1:-"help"}

if [ "$command" == "up" ]; then
    print_msg "🚀 Invoking Intelligent Azure Hardware Scheduler..."
    print_msg "Azure is experiencing catastrophic B-Series capacity exhaustion this weekend."
    print_msg "Booting aggressive multi-region fallback loop to bypass capacity restrictions automatically..."
    
    # We will loop through high-capacity Datacenters worldwide until we find open server racks
    REGIONS=("southcentralus" "eastus2" "westus3" "northeurope" "centralus" "eastus")
    SIZES=("Standard_B2s" "Standard_B2ms" "Standard_D2s_v3")
    
    DEPLOYED=false
    
    for LOCATION in "${REGIONS[@]}"; do
        for SIZE in "${SIZES[@]}"; do
            # RACE CONDITION FIX v2: Unique RG name per Region AND Size, so the inner size loop doesn't trip on its own async deletion!
            CLEAN_SIZE="${SIZE//_/-}"
            RG_NAME="rg-win-patch-${LOCATION}-${CLEAN_SIZE,,}-2027" 
            echo -e "\n\033[1;33m[Attempting]\033[0m Datacenter: \033[1m$LOCATION\033[0m | Hardware: \033[1m$SIZE\033[0m"
            
            # Silently create the RG in the target region
            az group create --name "$RG_NAME" --location "$LOCATION" -o none 2>/dev/null || true
            
            # Attempt deployment. Redirect stderr to capture the exact failure reason without crashing the loop.
            set +e
            ERROR_OUTPUT=$(az vm create \
                --resource-group "$RG_NAME" \
                --name "$VM_NAME" \
                --image "Win2019Datacenter" \
                --admin-username "$ADMIN_USER" \
                --admin-password "$ADMIN_PASS" \
                --size "$SIZE" \
                --storage-sku "Standard_LRS" \
                --nsg-rule "RDP" \
                --public-ip-sku "Basic" \
                --output none 2>&1)
            EXIT_CODE=$?
            set -e
            
            if [ $EXIT_CODE -eq 0 ]; then
                DEPLOYED=true
                print_msg "✅ SUCCESS! Hardware secured in $LOCATION using $SIZE!"
                break 2
            else
                if echo "$ERROR_OUTPUT" | grep -q -i "SkuNotAvailable\|Capacity"; then
                    echo "   ⚠️ Azure Rack Space Exhausted. Jumping to next..."
                    # Cleanup the orphaned RG in the background so it doesn't block the next region
                    az group delete --name "$RG_NAME" --yes --no-wait 2>/dev/null || true
                elif echo "$ERROR_OUTPUT" | grep -q -i "QuotaExceeded\|quota"; then
                    echo -e "\n❌ CRITICAL QUOTA ERROR: You do not have enough vCPUs permitted on your Azure Account to provision a $SIZE VM."
                    echo "You must delete an old lab (e.g., AKS Cluster) to free up CPU cores."
                    exit 1
                else
                    echo -e "\n❌ UNKNOWN ERROR: $ERROR_OUTPUT"
                    exit 1
                fi
            fi
        done
    done
    
    if [ "$DEPLOYED" == "false" ]; then
        echo -e "\n❌ ALL REGIONS EXHAUSTED. Azure cannot fulfill this request right now."
        exit 1
    fi
        
    print_msg "🔄 Enforcing 'Manual' patch orchestration for Azure Update Manager..."
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
    
    # Loop through all possible RGs we might have created and invoke async deletion
    az group list --query "[?contains(name, 'rg-win-patch')].name" -o tsv | while read -r rg; do
        if [ ! -z "$rg" ]; then
            echo -e "[1;33m⚠️ Nuking associated Resource Group: $rg...[0m"
            az group delete --name "$rg" --yes --no-wait 2>/dev/null || true
        fi
    done
    
    # Dummy condition to preserve syntax mapping
    if true; then
        az group delete --name "$RG_NAME" --yes --no-wait
        echo -e "\033[1;32m✅ Teardown initiated. Resources will be deleted safely in the background.\033[0m"
    else
        echo -e "\033[1;33m⚠️ Lab resource group '$RG_NAME' does not exist.\033[0m"
    fi
else
    print_msg "❌ Invalid command. Usage: curl -sSL <url> | bash -s -- [up|down]"
fi
