# 🚀 Lab Guide: RHEL 8.6 to 8.10 Minor Version Upgrade (Azure)

## 🧠 Core Concept: Minor vs. Major Upgrades
In the Red Hat Enterprise Linux ecosystem, upgrades are classified in two ways:
1. **Major Upgrade (e.g., RHEL 7 to RHEL 8):** Involves profound architectural shifts (new Kernels, switching from `yum` to `dnf`). This requires heavy, complex tooling like the **Leapp** framework to migrate data.
2. **Minor Upgrade (e.g., RHEL 8.6 to 8.10):** Focuses on security patches, backported features, and bug fixes while guaranteeing **ABI (Application Binary Interface) compatibility**. Applications running on 8.6 will run flawlessly on 8.10. 
   - This is natively executed via standard package managers (`dnf`).
   - Azure's **RHUI** (Red Hat Update Infrastructure) abstracts away standard Subscription Manager requirements, making this upgrade effortless on Pay-As-You-Go (PAYG) VMs.

---

## 🛠️ Step 1: Provision the Azure RHEL 8.6 Instance
Open the **Azure Cloud Shell (Bash)** and run the following commands to scaffold your environment.

### 1. Create a Resource Group
```bash
az group create --name RHEL-Upgrade-Lab-RG --location eastus
```

### 2. Locate the Exact RHEL 8.6 URN (Read-Only Step)
*(Azure Marketplace changes image references frequently. This command helps you locate the exact URN if the deployment string fails).*
```bash
az vm image list -p RedHat -f RHEL -s 8_6 --all --query "[0].urn" -o tsv
```

### 3. Deploy the Virtual Machine
We will deploy a `Standard_B2s` tier VM with an explicit RHEL 8.6 image.
```bash
az vm create \
  --resource-group RHEL-Upgrade-Lab-RG \
  --name rhel-node-01 \
  --image RedHat:RHEL:8_6:latest \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard \
  --size Standard_B2s
```
*(Copy the `publicIpAddress` from the JSON output once it completes)*

---

## 🔑 Step 2: Establish SSH and Pre-Flight Validation
Connect to your freshly minted RHEL 8.6 box using the public IP provided in the previous step.
```bash
ssh azureuser@<YOUR_PUBLIC_IP>
```

### Validate Initial State
Check the kernel version and the exact OS release string:
```bash
cat /etc/redhat-release
# Desired Output: Red Hat Enterprise Linux release 8.6 (Ootpa)

uname -r
# Note down the Kernel signature
```

---

## ⚙️ Step 3: Perform the Operational Upgrade
Since we are using Azure, the VM is pre-connected to RHUI. However, some 8.6 images may have the release locked to Extended Update Support (EUS).

### 1. Clear caches and release locks
```bash
# Verify if the version is locked to 8.6
sudo subscription-manager release --show

# Force the release lock to clear so it targets the latest 8.x repository (8.10)
sudo subscription-manager release --unset

# Clean the DNF cache for a fresh repository pull
sudo dnf clean all
```

### 2. Execute the Upgrade
Review the pending package updates, then trigger the upgrade.
```bash
# Preview what is about to change (Look for kernel and systemd updates)
sudo dnf check-update

# Run the upgrade
sudo dnf upgrade -y
```
*(This process will take 5-10 minutes as it downloads and unpacks hundreds of RPM packages across the networking, filesystem, and kernel namespaces).*

### 3. Apply the Kernel Patch
Because core kernel modules (`vmlinuz`) were just upgraded, the server **must** be rebooted for the hardware to inherit the 8.10 Kernel payload.
```bash
sudo reboot
```

---

## ✅ Step 4: Post-Flight Validation
Your SSH connection will drop. Wait 60 seconds and SSH back in.

```bash
ssh azureuser@<YOUR_PUBLIC_IP>
```

### 1. Verify OS Release
```bash
cat /etc/redhat-release
# Target Output: Red Hat Enterprise Linux release 8.10 (Ootpa)
```

### 2. Verify Kernel Upgrade
```bash
uname -r
# Compare this against your previous output to prove the kernel was updated.
```

### 3. Check for Broken Dependencies
Ensure that the upgrade did not break any core system libraries.
```bash
sudo dnf update
# Should read: "Dependencies resolved. Nothing to do. Complete!"
```

---

## 🗑️ Step 5: Clean Up / Teardown
Never leave sandbox infrastructure running. Return to your Azure Cloud Shell and nuke the resource group to stop billing.
```bash
az group delete --name RHEL-Upgrade-Lab-RG --yes --no-wait
```
