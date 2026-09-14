# ☁️ Securely Mounting Azure File Share (NFS 4.1) for Logrotate

In Enterprise Scenario 3, we utilized the `olddir` logrotate directive to shovel historical `.gz` archives off our fast VM SSDs and onto a cheaper storage drive:
`olddir /mnt/deep_archive/logs/`

The most cloud-native way to achieve this in Azure is using an **Azure Premium File Share (NFS)**. This acts as a highly scalable remote hard drive that multiple VMs can write logs to simultaneously.

Here is the exact blueprint for generating, securing, and mounting an Azure NFS share for `logrotate`.

---

## 🛠️ Phase 1: Provisioning the Azure NFS Share (Securely)

Unlike standard SMB file shares in Azure (which use Access Keys), **NFS 4.1 shares in Azure use strict network-level Zero-Trust security**. They *must* be deployed on a Premium Storage Account and explicitly locked to your VM's Virtual Network (VNet).

**Execute this via Azure CLI (or Terraform):**

```bash
# 1. Define your variables
RG="rg-logrotate-lab"
LOCATION="eastus"
VNET="vnet-logrotate"
SUBNET="snet-storage"
STORAGE_ACCT="stlogrotateext$(date +%s)"
SHARE_NAME="nfs-logs-archive"

# 2. Create the VNet and inject a Microsoft.Storage Service Endpoint
# This ensures traffic never traverses the public internet!
az network vnet create -g $RG -n $VNET --address-prefix 10.0.0.0/16 -l $LOCATION
az network vnet subnet create -g $RG --vnet-name $VNET -n $SUBNET --address-prefixes 10.0.1.0/24 --service-endpoints Microsoft.Storage

# 3. Create a PREMIUM FileStorage Account (Required for NFS)
az storage account create \
    --resource-group $RG \
    --name $STORAGE_ACCT \
    --location $LOCATION \
    --sku Premium_LRS \
    --kind FileStorage \
    --https-only false # NFS 4.1 on Azure is not encrypted in transit by default, it relies on strict VNet boundaries.

# 4. Lock the Storage Account explicitly to your Subnet (Zero-Trust Network Rule)
az storage account network-rule add \
    -g $RG --account-name $STORAGE_ACCT --vnet-name $VNET --subnet $SUBNET
az storage account update -g $RG -n $STORAGE_ACCT --default-action Deny

# 5. Create the NFS Share (100 GB Quota)
az storage share-rm create \
    --resource-group $RG \
    --storage-account $STORAGE_ACCT \
    --name $SHARE_NAME \
    --enabled-protocols NFS \
    --quota 100
```

---

## 🔒 Phase 2: Mounting to the Linux VM

SSH into the Linux Virtual Machine that is running `logrotate`. (Ensure this VM is running inside the same `$VNET` we deployed above).

```bash
# 1. Install the NFS utility packages
# For RHEL/AlmaLinux/CentOS:
sudo yum install -y nfs-utils

# 2. Create the deep archive directory exactly as referenced in our logrotate conf
sudo mkdir -p /mnt/deep_archive/logs

# 3. Mount the Azure NFS Share securely via fstab
# Open /etc/fstab to ensure the drive survives VM reboots
sudo nano /etc/fstab

# 4. Append this exact line to the bottom of the file:
# (Replace YOUR_STORAGE_ACCT with the generated $STORAGE_ACCT name)
YOUR_STORAGE_ACCT.file.core.windows.net:/YOUR_STORAGE_ACCT/nfs-logs-archive /mnt/deep_archive/logs nfs vers=4.1,sec=sys,nosuid,nodev,nofail 0 0

# Security Breakdown of the Mount Options:
# vers=4.1 : Mandates NFS v4.1 for Azure native support.
# nosuid   : Prevents users from escalating privileges using malicious binaries tucked in the logs.
# nodev    : Prevents interpreting character/block devices on the remote file system.
# nofail   : CRITICAL! If Azure has an outage, the VM will still boot up without getting stuck.

# 5. Apply the mount immediately without rebooting
sudo mount -a

# 6. Verify the cloud drive is attached!
df -h | grep /mnt/deep_archive/logs
```

---

## 🏃 Phase 3: Validating Logrotate's Handover

Because `logrotate` runs as `root`, it natively possesses the permissions to push files into this new remote Azure mount. 

If your `/etc/logrotate.d/my_app` has this injected:
```text
olddir /mnt/deep_archive/logs/
```

When you execute your diagnostic script (`sudo logrotate -vf /etc/logrotate.d/my_app`), you will see the `.gz` files instantly bypass the `/var/log` volume and appear sitting comfortably on your Azure Storage Account thousands of miles away!
