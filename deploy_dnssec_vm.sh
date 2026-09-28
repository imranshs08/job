#!/bin/bash
RG="rg-dnssec-lab"
REGIONS=("eastus" "westus2" "centralus" "northeurope" "westeurope" "eastasia")
SIZES=("Standard_B1s" "Standard_B2s" "Standard_D2s_v3" "Standard_DS1_v2")

for REGION in "${REGIONS[@]}"; do
    echo "Creating Resource Group in $REGION..."
    az group create --name $RG --location $REGION >/dev/null 2>&1
    
    for SIZE in "${SIZES[@]}"; do
        echo "Attempting to provision Ubuntu dns-victim VM on $SIZE in $REGION..."
        # Add --no-wait to bypass the Azure CLI Python requests bug? No we need the IP.
        # However if it creates, az vm show will work eventually.
        az vm create --resource-group $RG --name vm-dns-victim --image Ubuntu2204 --admin-username sreadmin --generate-ssh-keys --public-ip-sku Standard --size $SIZE > output.json 2> error.log
        
        if az vm show -g $RG -n vm-dns-victim &>/dev/null; then
            echo "SUCCESS: VM successfully spawned in $REGION on $SIZE"
            IP=$(az vm show -d -g $RG -n vm-dns-victim --query publicIps -o tsv)
            echo "Public IP: $IP"
            exit 0
        fi
        echo "Failed. Trying next size..."
    done
done
echo "All regions failed."
exit 1
