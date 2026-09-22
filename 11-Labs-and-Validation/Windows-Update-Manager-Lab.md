# ☁️ Lab: Azure Windows Server 2019 Patching & Update Manager

> **Role Context:** Senior DevOps/SRE
> **Objective:** Provision a cost-optimized Windows Server 2019 VM, validate missing KB patches, apply targeted security updates via Azure Update Manager, and teardown the environment safely.

---

## 1️⃣ 1-Click Infrastructure Deployment

We will deeply cost-optimize this VM by provisioning it as a `Standard_B2s` (Burstable CPU) mapping to standard magnetic storage (HDD). This avoids the heavy $100+/mo burn rates of D-Series Premium SSD machines.

**Provision the VM:**
```bash
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_win_patching_lab.sh" | bash -s -- up
```
*(Save the Username and Password payload returned by the script!)*

---

## 2️⃣ Navigating Azure Update Manager

Azure recently migrated away from the legacy Log Analytics "Automation Account" update management to the native **Azure Update Manager**. 

1. Go to the Azure Portal.
2. Search for **Update Manager** in the top search bar.
3. Click on **Machines** and select your `vm-win2019-lab`.
4. Click **Check for updates**. Azure will scan the virtual machine OS disk directly to identify missing Classifications (Critical, Security, Update Rollups).

---

## 3️⃣ Validating & Filtering KB Articles

In an enterprise environment, you NEVER apply all patches blindly. A specific KB (Knowledge Base) patch might break legacy IIS or .NET applications.

### How to analyze KBs:
1. In Update Manager, under **Pending Updates**, you will see a list of missing patches alongside their `KB ID` (e.g., `KB5031362`).
2. **Microsoft Update Catalog:** Google the KB ID and read the "Known Issues" section. If the known issues interfere with your specific workload, you block it.

### Applying Tailored KBs:
1. Click **One-time update** on the machine.
2. Select **Include / Exclude updates**.
3. **By Classification:** Uncheck "Feature Packs" and "Tools". Only select "Critical" and "Security".
4. **By KB Article:** Under the *Include/Exclude by KB* tab, you can physically type the `KB Number` you want to either specifically target or explicitly ban from being installed.
5. Set the **Reboot Option** to `Reboot if required`.

### Validating Success via PowerShell (In the VM)
To strictly validate if a KB actually applied successfully within the Windows OS, RDP into the box and run:
```powershell
# Lists all installed hotfixes and their exact installation date
Get-HotFix | Select-Object HotFixID, InstalledOn, Description | Sort-Object InstalledOn -Descending

# Check if a specific KB exists
Get-HotFix -Id KB5031362
```

---

## 4️⃣ Infrastructure Teardown

Never leave Windows VMs running when idle. Destroy the lab using the exact same webhook:

**Delete the VM and Resource Group:**
```bash
curl -sSL "https://raw.githubusercontent.com/imranshs08/job/main/16-Automation-Scripts/azure_win_patching_lab.sh" | bash -s -- down
```
