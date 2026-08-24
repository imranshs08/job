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

### 1. Set your Sandbox Resource Group
*(Your sandbox dynamically generates a new Resource Group string every session. Use bash sub-shell expansion to automatically fetch and export it).*
```bash
export SANDBOX_RG=$(az group list --query "[0].name" -o tsv)
echo "Active Sandbox Resource Group: $SANDBOX_RG"
```

### 2. Export the Active RHEL 8.6 URN
*(Azure Marketplace frequently cycles image references. Use sub-shell expansion to assign the live URN dynamically).*
```bash
export RHEL_URN=$(az vm image list -p RedHat -f RHEL -s 8_6 --all --query "[0].urn" -o tsv)
echo "Active Image URN: $RHEL_URN"
```

### 3. Deploy the Virtual Machine
We will deploy a `Standard_B2s` tier VM (which is guaranteed to be whitelisted by your Sandbox).
```bash
az vm create \
  --resource-group "$SANDBOX_RG" \
  --name rhel-node-01 \
  --image "$RHEL_URN" \
  --admin-username azureuser \
  --admin-password "KodeKloud@2027!" \
  --size Standard_B2s
```
*(Copy the `publicIpAddress` from the JSON output once it completes)*

### 4. ⚡ Optional: The One-Click Quick Deployment Script
*(If you want to skip manually running steps 1-3, simply copy and paste this unified block straight into your Cloud Shell).*
```bash
export SANDBOX_RG=$(az group list --query "[0].name" -o tsv)
export RHEL_URN=$(az vm image list -p RedHat -f RHEL -s 8_6 --all --query "[0].urn" -o tsv)

az vm create \
  --resource-group "$SANDBOX_RG" \
  --name rhel-node-01 \
  --image "$RHEL_URN" \
  --admin-username azureuser \
  --admin-password "KodeKloud@2027!" \
  --size Standard_B2s
```

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
Never leave sandbox infrastructure running. Since you are in a protected Sandbox, simply closing the training session will automatically purge the resources.
```bash
# If running on a personal account, you would normally run:
# az group delete --name <YOUR_SANDBOX_RG> --yes --no-wait
```

---

## 🚀 Advanced Tier: Major Upgrade (RHEL 8 ➡️ RHEL 9)
If you decide you want to upgrade your freshly minted `8.10` machine completely into the `RHEL 9.x` architecture, `dnf upgrade` is instantly useless. You must rely on Red Hat's **Leapp Framework**, which handles deep architectural and Python binary shifts.

### 1. Azure-Specific Leapp Preparation
In Azure, the Pay-As-You-Go VMs route through specialized RHUI servers. You cannot upgrade without installing the Azure-specific RHUI routing packages designed for RHEL 9.

```bash
# Remove the old RHEL 8 cloud configurations
sudo dnf remove -y rhui-azure-rhel8 

# Install the Leapp upgrade architecture and Azure's RHEL 9 RHUI package
sudo dnf install -y rhui-azure-rhel9 leapp-upgrade
```

### 2. The Leapp Pre-Upgrade Assessment
Never run a major upgrade blindly. The framework first analyzes your OS, hardware drivers, and installed software to predict if a migration will crash the server.

```bash
sudo leapp preupgrade --no-rhsm
```
*If this fails, you must open `/var/log/leapp/leapp-report.txt` to find and resolve the blocking anomalies (e.g., deprecated Python packages, incompatible third-party drivers) before proceeding.*

### 3. Execution & The Transitional Ramdisk
Once the pre-upgrade passes smoothly, initialize the structural transition:

```bash
sudo leapp upgrade --no-rhsm
```
*(This downloads the massive RHEL 9 payloads and configures them securely into a boot partition).*

```bash
sudo reboot
```
*During reboot, the VM boots into a temporary **Leapp Upgrade Ramdisk environment (Initramfs)** where the real magic happens. SSH will be completely dead for 15-30 minutes while packages are extracted and the RHEL 8 binaries are systematically destroyed and replaced by RHEL 9.*

### 4. Final Validation
Once SSH comes back alive, authenticate and verify you have successfully crossed into a new Major architecture tier!

```bash
cat /etc/redhat-release
# Desired Output: Red Hat Enterprise Linux release 9.x (Plow)
```
