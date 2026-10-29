# 🛡️ Enterprise RHEL 8.10 Deterministic Patch Management Lab
> **Zero-Drift Patch Automation across Dev, Preprod, and Prod using Ansible, DNF Snapshots & AWX**

---

## 🎯 Executive Overview & The Problem

In enterprise environments with phased patch rollout schedules (e.g., **Dev** patched in Week 1, **Preprod** in mid-month, and **Prod** in Week 4), executing direct online commands like `dnf upgrade --security` introduces **severe package drift**.

```
Upstream Red Hat CDN (Packages update continuously)
       │
       ├─► [Day 05] Dev Patches      ──► Receives Patch Set A
       ├─► [Day 18] Preprod Patches  ──► Receives Patch Set A + B (B never tested in Dev!)
       └─► [Day 28] Prod Patches     ──► Receives Patch Set A + B + C (Unvalidated code in Prod!)
```

### The "Moving Target" Trap
* Running `dnf upgrade --security` fetches whatever errata are live *on the exact day the command runs*.
* A bug introduced in a mid-month Red Hat advisory can pass directly into Production without ever being caught in Dev or Preprod.
* **The SRE Golden Rule:** *All environments in a patching cycle must consume from an identical, frozen, immutable package snapshot.*

---

## 🏛️ Architecture & Solution Matrix

| Strategy | Mechanism | Enterprise Fit | Lab Viability |
| :--- | :--- | :--- | :--- |
| **Option A: Red Hat Satellite / Katello** | **Content Views (CVs)**: Sync once on the 1st of the month; promote the snapshot across Lifecycle Environments (`Library -> Dev -> QA -> Prod`). | Standard in large RHEL estates | Heavy (~20GB RAM, requires Red Hat subscription) |
| **Option B: Frozen Repo Mirror (reposync + Nginx)** | Sync upstream RPMs on the 1st of each month into a dated folder (`/repos/snapshots/2026-10/`). All targets lock their baseurl to this directory. | **Best practice for lean enterprises & cloud VPCs** | **Lightweight, 100% deterministic, zero cost** |
| **Option C: DNF Versionlock / Lockfile** | Export installed package manifest from Dev and lock with `python3-dnf-plugin-versionlock` across Preprod/Prod. | Temporary tactical fix | Does not solve upstream repo package pruning |

---

## 🧪 Local Lab Architecture

This lab runs **6 simulated RHEL 8.10 target nodes** (using binary-compatible AlmaLinux 8.10 containers with OpenSSH and systemd tools) and **1 internal repository mirror (Nginx)** on a private bridge network.

```
                      ┌──────────────────────────────────────────────┐
                      │          Ansible Control Node / AWX          │
                      │           (Executes Playbook Cycle)          │
                      └──────────────────────┬───────────────────────┘
                                             │ SSH (Ports 2201-2206)
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Local Repo Mirror (Nginx Container)       │
                      │   URL: http://repo-server:80/repos/snapshots │
                      └───────┬──────────────┬──────────────┬────────┘
                              │              │              │
              ┌───────────────┘              │              └───────────────┐
              ▼                              ▼                              ▼
      [ Dev Environment ]           [ Preprod Env ]                 [ Prod Env ]
    ┌───────────────────┐         ┌───────────────────┐          ┌───────────────────┐
    │ rhel-01 : rhel-02 │         │ rhel-03 : rhel-04 │          │ rhel-05 : rhel-06 │
    │ (Port 2201, 2202) │         │ (Port 2203, 2204) │          │ (Port 2205, 2206) │
    └───────────────────┘         └───────────────────┘          └───────────────────┘
```

---

## 📂 Repository Structure

```text
10-RHEL-Enterprise-Patch-Management/
├── README.md                      # Architecture, execution guide, and SRE best practices
├── docker-compose.yml             # Orchestration for 6 target nodes + 1 repo server
├── Dockerfile.target              # RHEL 8.10 / AlmaLinux 8.10 SSH target container
├── repo-server/
│   └── nginx.conf                 # Nginx configuration serving repo snapshots
├── scripts/
│   └── freeze-repo-snapshot.sh    # Syncs RPMs and generates immutable monthly baseline
└── ansible/
    ├── ansible.cfg                # Tuned Ansible config with pipelining and host key bypass
    ├── hosts.ini                  # Tiered inventory: [dev], [preprod], [prod]
    ├── patch-pipeline.yml         # 5-phase deterministic patching playbook
    └── rollback.yml               # Automated rollback playbook via `dnf history undo`
```

---

## 🚀 Quickstart: Running the Local Lab

### Prerequisites
* Docker & Docker Compose installed
* Ansible installed (on host or inside WSL2)

### Step 1: Spin up the 6-Node Fleet & Repo Server
```bash
cd 11-Labs-and-Validation/10-RHEL-Enterprise-Patch-Management

# Build and start the containers
docker-compose up -d --build

# Verify all 7 containers are healthy
docker-compose ps
```

### Step 2: Generate the Monthly Snapshot
On the 1st of the month, run the snapshot sync:
```bash
bash scripts/freeze-repo-snapshot.sh 2026-10
```
This generates the frozen directory:
`repo-data/snapshots/2026-10/{BaseOS,AppStream}` served at `http://172.28.0.10:80/repos/snapshots/2026-10/`.

---

## 🔄 The Phased Enterprise Patching Cycle

### Phase 1: Week 1 — Patching Dev
In Week 1, run the Ansible pipeline targeting the `dev` environment:
```bash
ansible-playbook -i ansible/hosts.ini ansible/patch-pipeline.yml \
  -e "target_env=dev" \
  -e "active_patch_snapshot=2026-10" \
  -e "batch_size=100%"
```
* **Actions:**
  1. Validates disk space (`/` and `/var` >= 2.5 GB).
  2. Points `rhel-01` and `rhel-02` to the `2026-10` snapshot.
  3. Disables live upstream mirrors.
  4. Runs `dnf upgrade --security` against the frozen repo.
  5. Performs a conditional reboot if `needs-restarting -r` exits non-zero.
  6. Validates services (`sshd`, `crond`) and checks for broken dependencies (`dnf check`).
* **Validation Period:** Dev team runs regression tests for 7 days.

---

### Phase 2: Mid-Month — Patching Preprod
Once Dev has validated the patch set, trigger Preprod with the **exact same snapshot**:
```bash
ansible-playbook -i ansible/hosts.ini ansible/patch-pipeline.yml \
  -e "target_env=preprod" \
  -e "active_patch_snapshot=2026-10" \
  -e "batch_size=50%"
```
* **Key Difference:** `batch_size=50%` ensures only one node reboots at a time (`rhel-03`, then `rhel-04`), preserving service availability.
* **Result:** Preprod receives **100% identical package versions** to Dev, even though 2 weeks have passed since Dev was patched.

---

### Phase 3: Month-End — Patching Production
In the maintenance window at the end of the month:
```bash
ansible-playbook -i ansible/hosts.ini ansible/patch-pipeline.yml \
  -e "target_env=prod" \
  -e "active_patch_snapshot=2026-10" \
  -e "batch_size=50%"
```
* **Parity Guarantee:** Prod pulls strictly from the `2026-10` snapshot tested in Dev and Preprod. Zero unvetted packages can leak into Production.

---

## 🚨 Emergency Rollback Playbook

If an application fails health checks post-patch, execute the automated rollback:
```bash
ansible-playbook -i ansible/hosts.ini ansible/rollback.yml \
  -e "target_env=dev" \
  -e "batch_size=50%"
```
This runs `dnf history undo last -y` and conditionally reboots the node back to its pre-patch kernel and library state.

---

## 🏢 AWX / Red Hat Ansible Automation Platform Integration

To operationalize this in AWX:

1. **Create an AWX Project** pointing to this Git repository.
2. **Create Three Job Templates**:
   * `Job-Patch-Dev`: Variable `target_env: dev`, `batch_size: 100%`
   * `Job-Patch-Preprod`: Variable `target_env: preprod`, `batch_size: 50%`
   * `Job-Patch-Prod`: Variable `target_env: prod`, `batch_size: 50%`
3. **Build an AWX Workflow Template**:
   ```
   [Run Job-Patch-Dev]
           │ (On Success)
           ▼
   [Wait 7 Days / Approval Gate]
           │ (Approved)
           ▼
   [Run Job-Patch-Preprod]
           │ (On Success)
           ▼
   [Wait 7 Days / Approval Gate]
           │ (CAB Sign-off)
           ▼
   [Run Job-Patch-Prod]
   ```

---

## 💡 Production Gotchas & SRE Interview Traps

1. **The Epel & Third-Party Trap:**
   * If third-party repositories (EPEL, Docker-CE, HashiCorp, CrowdStrike) are left pointing to public dynamic mirrors, your servers will still experience package drift.
   * *Fix:* All external repositories must either be disabled during OS security windows or synced into your internal snapshot repository.
2. **The "Disk Full Mid-Transaction" Nightmare:**
   * If `/var` or `/` runs out of space while RPM is installing files, the RPM database (`/var/lib/rpm`) becomes corrupted, leaving duplicate package entries.
   * *Defense:* Phase 1.2 enforces an assertion requiring at least 2.5 GB free space before DNF is even invoked.
3. **The Kernel ABI / Third-Party Driver Trap:**
   * Updating the Linux kernel can break proprietary kernel modules (NVIDIA drivers, SAN multipathing, antivirus sensor agents).
   * *Defense:* Track kernel updates separately and ensure `kmod` or `akmods` packages are tested in Dev before rolling to Prod.
4. **Reboot Determination:**
   * Never rely on naive assumptions about whether a reboot is needed. Always query `needs-restarting -r` from the `yum-utils` package:
     * Exit code `0` = No reboot required (services can be reloaded).
     * Exit code `1` = Reboot required (core libraries like `glibc` or `systemd` or the `kernel` were modified).
