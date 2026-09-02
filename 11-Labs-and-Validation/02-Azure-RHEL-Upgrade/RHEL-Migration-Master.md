# 🔴 Red Hat Enterprise Linux (RHEL) Lifecycle & Upgrade Methodology

This document serves as the master reference guide for understanding the Red Hat Enterprise Linux release cycle, end-of-life (EOL) timelines, and the precise mechanical processes required to execute patches, minor version bumps, and major version upgrades.

---

## 📅 The RHEL Release Cycle Architecture

Red Hat employs a strictly predictable, time-based release cadence to ensure enterprise stability while continuously delivering modern features.

*   **Major Releases (e.g., RHEL 8, RHEL 9):** Released approximately every **3 years**. Major releases introduce significant architectural changes, new kernels, and updated system libraries.
*   **Minor Releases (e.g., 8.6, 8.10, 9.4):** Released precisely every **6 months** (typically May and November). They introduce non-breaking feature enhancements, hardware enablement, and bug fixes without altering the core Application Binary Interface (ABI).

### The 10-Year Support Lifecycle
A modern RHEL major version (RHEL 8 & 9) is supported for **10 years**, divided into two distinct phases:

1.  **Full Support (Years 1-5):** Active development. Includes new hardware enablement, new software features, and critical security patches.
2.  **Maintenance Support (Years 6-10):** Hardened stability. No new features. Only critical/important security patches and urgent bug fixes are released.

> [!TIP]
> **Extended Update Support (EUS)**
> For enterprises that cannot upgrade minor versions every 6 months, Red Hat offers EUS. An EUS release (usually even numbers like 8.4, 8.6, 9.2, 9.4) allows you to stay on that specific minor version and receive critical security patches for up to **24 months** without breaking applications.

### ☁️ Cloud-Native (PAYG) vs On-Premise Subscriptions
A critical architectural difference exists between physical datacenters and Cloud (Azure/AWS) RHEL deployments:
*   **On-Premise / BYOL:** You must forcefully authenticate a machine to Red Hat via the `subscription-manager` utility to pull packages. If a release lock occurs, you use `subscription-manager release --unset`.
*   **Cloud-Native PAYG:** Azure natively injects a background engine called **RHUI (Red Hat Update Infrastructure)**. RHUI completely bypasses the local `subscription-manager` binary. If a Cloud VM gets stuck on a deprecated EUS minor branch, you cannot use `subscription-manager` to fix it. You must physically delete the lock file (`/etc/yum/vars/releasever`) and reinstall the Cloud-native repository RPMs (e.g., `rhui-azure-rhel8`).

---

## ⏳ Critical End-of-Life (EOL) Timelines

Understanding when a product transitions into EOL is critical for security compliance and Zero-Trust architecture.

| Version | Full Support Ended | Maintenance Support Ends (EOL) | Extended Life Cycle (ELC) Ends |
| :--- | :--- | :--- | :--- |
| **RHEL 7** | August 6, 2019 | **June 30, 2024** | June 30, 2028 |
| **RHEL 8** | May 31, 2024 | **May 31, 2029** | May 31, 2032 |
| **RHEL 9** | May 31, 2027 | **May 31, 2032** | May 31, 2036 |

🔗 **Official Telemetry Sources:**
*   [Red Hat Enterprise Linux Life Cycle (Official Portal)](https://access.redhat.com/support/policy/updates/errata)
*   [Azure RHEL Image Lifecycle Documentation](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/rhel-images)

---

## 🚀 Upgrade Methodologies

System upgrades in Red Hat are categorized into three distinct tiers of operational risk.

### 1. Patching (Routine Maintenance)
*   **Definition:** Installing the latest security fixes and bug patches for the *current* minor release.
*   **Risk Level:** Extremely Low.
*   **Execution:** 
    ```bash
    # Review what will be patched
    sudo dnf check-update --security
    
    # Apply all security patches only
    sudo dnf update --security -y
    
    # Or, apply all available patches (recommended in staging)
    sudo dnf update -y
    ```

### 2. Minor Upgrades (e.g., 8.6 to 8.10)
*   **Definition:** Moving from an older 6-month release loop to the latest minor version within the same Major architectural family.
*   **Risk Level:** Low to Medium.
*   **Execution:** Since the Application Binary Interface (ABI) is guaranteed not to break, minor upgrades are typically seamless operations executed via the native package manager.
    ```bash
    # Flush the local daemon caches
    sudo dnf clean all
    
    # Execute the OS replacement pipeline
    sudo dnf upgrade -y
    
    # Reboot to load the new Kernel
    sudo reboot
    ```

### 3. Major Upgrades (e.g., RHEL 8 to RHEL 9)
*   **Definition:** A complete architectural transition replacing the core Kernel, GCC compilers, system libraries, and base runtimes.
*   **Risk Level:** High (Requires Pre-Flight testing).
*   **Execution:** Major upgrades cannot be performed with `dnf`. They utilize a dedicated Python-based framework called **Leapp** that calculates a massive dependency matrix, generates a pre-upgrade risk report, creates a dedicated `initramfs` bootloader, and swaps the entire OS out during a system restart.
    ```bash
    # (Azure) Install the Leapp Framework and the Azure Cloud Integration Plugin
    sudo dnf install -y leapp-upgrade leapp-rhui-azure
    
    # Generate the Pre-Upgrade Risk Assessment Report (Bypass Subscription Manager)
    sudo leapp preupgrade --no-rhsm
    
    # Review the report generated at /var/log/leapp/leapp-report.txt
    # Mitigate any blocking issues.
    
    # Execute the massive OS transition payload
    sudo leapp upgrade --no-rhsm
    
    # Reboot into the Leapp Initramfs to overwrite the OS
    sudo reboot
    ```

> [!CAUTION]
> **Hunting Leapp Inhibitors (Blockers)**
> Leapp evaluates everything inside `/var/log/leapp/leapp-report.txt`. If it detects **even one** `Inhibitor` (a fatal blocker), the `leapp upgrade` command will refuse to execute to prevent system destruction.
> 
> **How to find them instantly without reading thousands of lines:**
> ```bash
> sudo grep -i inhibitor /var/log/leapp/leapp-report.txt -A 10
> ```
> **Common Fixes:**
> 1. **The Answerfile**: Leapp often halts to ask permission to delete legacy PAM modules. You fix this by typing `True` inside `/var/log/leapp/answerfile` to grant it deletion rights.
> 2. **Root SSH**: RHEL 9 hardens SSH defaults. Leapp may block the upgrade if your `sshd_config` allows loose root capabilities, requiring you to lock it down before proceeding.
> 
> *Always re-run `leapp preupgrade` until it prints "No inhibitors found" before pulling the trigger.*

---

## 🛡️ Enterprise Rollback Architectures (Disaster Recovery)

A Senior Platform Engineer never executes an upgrade without a mathematically proven rollback strategy. Because RHEL upgrades touch the kernel layer, rollback complexity scales aggressively with the upgrade type.

### 1. Patch Upgrade Rollback (Low Severity)
If a single security patch or minor library update breaks a running application (e.g., a bad Python bump), you can cleanly reverse it natively via DNF's transaction tracking.

```bash
# 1. Identity the transaction ID of the bad patch
sudo dnf history

# 2. Reverse that specific transaction mechanically
sudo dnf history undo <TRANSACTION_ID>
```

### 2. Minor Version Upgrade Rollback (Medium Severity)
Minor upgrades (8.6 ➡️ 8.10) mutate hundreds of packages at once. While `dnf history rollback` *technically* exists, it is highly discouraged for bulk OS bumps because complex library dependencies often shatter during reversal.

**The Enterprise Standard (LVM Snapshots):**
Before triggering `dnf upgrade -y`, you take an LVM snapshot of the `/root` volume. If the OS acts erratically post-upgrade, you reboot into the snapshot.
```bash
# Pre-Flight: Create a 10GB LVM snapshot named "pre-8.10-bump"
sudo lvcreate --size 10G --snapshot --name pre-8.10-bump /dev/mapper/rhel-root

# Post-Flight (Disaster): Merge the snapshot back into the root volume and reboot
sudo lvconvert --merge /dev/mapper/rhel-pre-8.10-bump
sudo reboot
```

### 3. Major Version Upgrade Rollback (Catastrophic Severity)
If a RHEL 8 ➡️ RHEL 9 `leapp` migration fails midway through the Initramfs payload, the operating system is effectively **destroyed**. 

> [!CAUTION]
> **Leapp is a One-Way Street**
> There is **NO** native OS rollback for `leapp`. Once the binaries are overwritten, the OS cannot un-upgrade itself.

**The Enterprise Standard (Hypervisor / Cloud Snapshots):**
The only way to survive a failed Major Upgrade is by utilizing immutable infrastructure backups explicitly decoupled from the RHEL OS layer.
*   **Azure / AWS / GCP:** Take a full VM Snapshot of the OS Disk inside the Cloud console before running Leapp. If it crashes, detach the broken OS disk, spawn a new disk from the Snapshot, and reattach it.
*   **On-Premise (VMware):** Create a vCenter Snapshot. Click "Revert to Snapshot" if the Ramdisk kernel panics.

### 🥇 The Golden Rule of Upgrades
**"If you do not have a snapshot of the root volume, you do not have permission to upgrade the Kernel."**

---
*Generated by the DevOps Command Center Bot for the AZ-104 & CKA 2027 Mastery Sprint.*


---


# 🚀 Lab Guide: RHEL Minor & Major Architecture Migrations (Azure)

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

> [!CAUTION]
> **Enterprise Rollback Architecture**
> Because this is a Minor Upgrade, `dnf history undo` is highly volatile for core packages. The Golden Rule dictates that you **must** have an LVM Snapshot (`lvcreate --snapshot`) of the `/root` logical volume before pulling this trigger. *(Since this is a disposable Sandbox, you are authorized to ignore this rule).*

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

> [!WARNING]
> **Troubleshooting Leapp Inhibitors**
> On Azure RHEL 8 instances, Leapp will almost always halt with an "Inhibitor" regarding the Firewalld `AllowZoneDrifting` configuration, because RHEL 9 deprecates this feature.
> 
> *To find the exact inhibitor in the massive log file:*
> ```bash
> sudo grep -i inhibitor /var/log/leapp/leapp-report.txt -A 10
> ```
> 
> *To fix the Firewalld blocker, inject this Red Hat approved `sed` string and re-run the assessment:*
> ```bash
> sudo sed -i s/^AllowZoneDrifting=.*/AllowZoneDrifting=no/ /etc/firewalld/firewalld.conf
> 
> sudo leapp preupgrade --no-rhsm
> ```

### 3. Execution & The Transitional Ramdisk
Once the pre-upgrade passes smoothly, you must explicitly look for the following authorization output at the bottom of the report:
```text
Reports summary:
    Errors:                      0
    Inhibitors:                  0
```

> [!CAUTION]
> **Catastrophic Rollback Architecture**
> `Leapp` is mathematically a **One-Way Street**. There is no OS-level rollback. If the initramfs kernel panics, the node is dead. You **MUST** have an immutable Cloud Hypervisor Snapshot of the OS disk to survive a failure. *(Since this is a disposable Sandbox, proceed fearlessly!).*

With zero inhibitors blocking the transition, initialize the structural transition:

```bash
sudo leapp upgrade --no-rhsm
```
*(This downloads the massive RHEL 9 payloads and configures them securely into a boot partition).*

```bash
sudo reboot
```

> [!WARNING]
> **The Invisible OS Swap**
> When you issue the reboot command, your SSH session will violently terminate. **DO NOT PANIC.** The server is not dead. It is actively booting into an invisible, temporary **Leapp Upgrade Ramdisk (Initramfs)**. 
> 
> *During this phase (10-30 minutes), the RHEL 8 binaries are being systematically stripped and replaced by RHEL 9. Wait patiently until the node responds to pings again before establishing a fresh SSH session.*

### 4. Final Validation
Once SSH comes back alive, authenticate and verify you have successfully crossed into a new Major architecture tier!

```bash
cat /etc/redhat-release
# Desired Output: Red Hat Enterprise Linux release 9.x (Plow)
```
