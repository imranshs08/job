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
