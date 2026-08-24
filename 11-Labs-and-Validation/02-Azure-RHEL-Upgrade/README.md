# 🚀 Lab Guide: RHEL 8.6 to 8.10 Minor Version Upgrade (Azure)

## 📚 Architect's Reference: RHEL Lifecycles & Upgrade Topology
> [!NOTE]
> Before triggering a destructive OS upgrade, Senior Engineers must mathematically understand the architectural boundary between an ABI-Stable Minor Update and a Kernel-swapping Major Migration. 
> 
> For the exhaustive master reference on RHEL's **10-Year EOL Matrix**, **EUS Locks**, and the mechanical differences between `dnf` and `leapp`, study the core documentation node:
> 👉 [**Red Hat (RHEL) Lifecycle & Upgrade Methodology**](../../04-Notes/rhel-lifecycle.md)

---
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
  --name rhel-node-02 \
  --image "$RHEL_URN" \
  --admin-username azureuser \
  --admin-password "KodeKloud@2027!" \
  --size Standard_B2s \
  --storage-sku Standard_LRS
```
*(Copy the `publicIpAddress` from the JSON output once it completes)*

### 4. ⚡ Optional: The One-Click Quick Deployment Script
*(If you want to skip manually running steps 1-3, simply copy and paste this unified block straight into your Cloud Shell).*
```bash
export SANDBOX_RG=$(az group list --query "[0].name" -o tsv)
export RHEL_URN=$(az vm image list -p RedHat -f RHEL -s 8_6 --all --query "[0].urn" -o tsv)

az vm create \
  --resource-group "$SANDBOX_RG" \
  --name rhel-node-02 \
  --image "$RHEL_URN" \
  --admin-username azureuser \
  --admin-password "KodeKloud@2027!" \
  --size Standard_B2s \
  --storage-sku Standard_LRS
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
# Target Baseline Kernel: 4.18.0-372.9.1.el8.x86_64
```

---

## ⚙️ Step 3: Perform the Operational Upgrade
Since we are using Azure, the VM is pre-connected to RHUI. However, some 8.6 images may have the release locked to Extended Update Support (EUS).

### 1. Flush the Local Cache
```bash
# Clean the DNF cache for a fresh repository pull
sudo dnf clean all
```

> [!WARNING]
> **Troubleshooting `Status code: 400` Errors**
> If your Sandbox deployed an image where the Extended Update Support (EUS) certificates have expired, `dnf clean all` or `upgrade` will crash with **Status code: 400**. To fix this, you must nuke the EUS lock and fetch the master repositories directly from Azure Blob:
> ```bash
> sudo rm -f /etc/yum/vars/releasever /etc/dnf/vars/releasever
> sudo dnf --disablerepo='*' remove -y rhui-azure-rhel8-eus
> sudo dnf --config='https://rhelimage.blob.core.windows.net/repositories/rhui-microsoft-azure-rhel8.config' install -y rhui-azure-rhel8
> sudo dnf clean all
> ```

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

## 🗑️ Step 5: Clean Up (Emergency Reset)
If your deployment fails midway or you want to start over *without* closing the active Sandbox session, you cannot delete the entire Resource Group (since KodeKloud owns it). Instead, you must surgically delete the VM and its orphaned dependencies (Disks, NICs, Public IPs). 

Run this advanced Bash pipeline to cleanly hunt down and purge every resource attached to the `rhel-node-02` prefix:

```bash
export SANDBOX_RG=$(az group list --query "[0].name" -o tsv)

# Fetch all resources matching the VM name and systematically delete their IDs
az resource list \
  --resource-group "$SANDBOX_RG" \
  --query "[?starts_with(name, 'rhel-node-01')].id" \
  -o tsv | xargs -r -n1 az resource delete --ids
```
*(If you are done for the day, you can skip this. KodeKloud automatically vaporizes everything when the session timer hits zero).*

---

## 🚀 Advanced Tier: Major Upgrade (RHEL 8 ➡️ RHEL 9)
If you decide you want to upgrade your freshly minted `8.10` machine completely into the `RHEL 9.x` architecture, `dnf upgrade` is instantly useless. You must rely on Red Hat's **Leapp Framework**, which handles deep architectural and Python binary shifts.

### 1. Azure-Specific Leapp Preparation
In Azure, the Pay-As-You-Go VMs route through specialized RHUI servers. You cannot upgrade without installing the Azure-specific RHUI routing packages designed for RHEL 9.

```bash
# Remove the old RHEL 8 cloud configurations
sudo dnf remove -y rhui-azure-rhel8 

# Install the Leapp upgrade architecture and Azure's native RHUI integration plugin
sudo dnf install -y leapp-upgrade leapp-rhui-azure
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
