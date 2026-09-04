# 🔥 Production-Grade Terraform Debugging Guide

> **Template Prompt:**
> *"My CI/CD pipeline failed with the following Terraform issue: [describe]. Backend: [S3/AzureRM]. Version: [version]. Error: [paste error]. Provide a step-by-step debugging approach with terraform CLI commands."*

---

## 🎯 Scenario: Terraform Pipeline Blocked by State Lock

- **Cloud/Backend:** AWS S3 + DynamoDB (or Azure Storage)
- **Version:** Terraform 1.5.7
- **Symptom:** The Jenkins/GitHub Actions pipeline halts at `terraform plan` or `apply` because the state is locked.

---

## 📋 Phase 1: Triage — Confirm the Problem

### Step 1.1 — Check the CI/CD Pipeline Logs

**Actual Output:**
```
$ terraform plan -out=tfplan
Acquiring state lock. This may take a few moments...

Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional request failed
Lock Info:
  ID:        a1b2c3d4-e5f6-7890-1234-56789abcdef0
  Path:      my-terraform-states/prod/network/terraform.tfstate
  Operation: OperationTypeApply
  Who:       jenkins@ci-agent-003
  Version:   1.5.7
  Created:   2026-09-04 10:15:22.123456 +0000 UTC
  Info:      

Terraform acquires a state lock to protect the state from being written
by multiple users at the same time. Please resolve the issue above and try
again.
```

> 🔴 **Red Flag:** A previous run (`OperationTypeApply` by `jenkins@ci-agent-003`) crashed, timed out, or was manually cancelled without releasing the lock cleanly.

---

## 📋 Phase 2: Deep Dive — Investigate the Lock Source

### Step 2.1 — Verify if Anyone is Actively Running Apply

Before we break the lock, we must **100% guarantee** that `jenkins@ci-agent-003` is not actually still running a legitimate apply. Force-unlocking while another process is writing to the state will cause **State Corruption**.

1. **Check the CI/CD tool (Jenkins/GitHub Actions):**
   - Look for aborted or timed-out builds from `2026-09-04 10:15:22 UTC`.
   - Confirm the job is fully killed.

2. **Check Cloud Provider Activity (Optional):**
   - Validate there are no mutating writes actively happening via CloudTrail (AWS) or Activity Log (Azure).

### Step 2.2 — Inspect the DynamoDB/Azure Lock Table Directly

(If you want to manually verify the stale lock in AWS):
```bash
aws dynamodb get-item \
  --table-name terraform-state-locks \
  --key '{"LockID": {"S": "my-terraform-states/prod/network/terraform.tfstate"}}'
```

**Actual Output:**
```json
{
    "Item": {
        "Info": {
            "S": "{\"ID\":\"a1b2c3d4-e5f6-7890-1234-56789abcdef0\",\"Operation\":\"OperationTypeApply\",\"Who\":\"jenkins@ci-agent-003\"}"
        },
        "LockID": {
            "S": "my-terraform-states/prod/network/terraform.tfstate"
        }
    }
}
```

---

## 📋 Phase 3: The Fix (Force Unlock)

Once confirmed that NO active process is using the state, run `terraform force-unlock`.

### Step 3.1 — Re-init locally or target the backend

```bash
# If doing this locally, authenticate to AWS/Azure and init first
terraform init
```

### Step 3.2 — Execute the Force Unlock using the Lock ID

```bash
# Syntax: terraform force-unlock [LOCK_ID]
terraform force-unlock a1b2c3d4-e5f6-7890-1234-56789abcdef0
```

**Actual Output:**
```
Do you really want to force-unlock?
  Terraform will remove the lock on the remote state.
  This will allow local Terraform commands to modify this state, even though it
  may be still in use. Only 'yes' will be accepted to confirm.

  Enter a value: yes

Terraform state has been successfully unlocked!
```

> ⚠️ **CRITICAL INTERVIEW POINT:** Emphasize that `force-unlock` is a destructive emergency command. Doing this haphazardly corrupts infrastructure.

---

## 📋 Phase 4: Dealing with State Corruption (Worst Case Scenario)

What if the pipeline crashed *mid-write* and the remote state file (`.tfstate`) is now corrupted or empty?

### Step 4.1 — Verify State Integrity

```bash
terraform state list
```
**Actual Output:**
```
Error: Failed to load state: state is empty or corrupted
```

### Step 4.2 — Restore from S3/Azure Blob Versioning

If backend versioning is (correctly) enabled:

1. List the S3 Object Versions:
```bash
aws s3api list-object-versions \
  --bucket my-terraform-states \
  --prefix prod/network/terraform.tfstate
```

2. Download the last known good version (prior to the crash):
```bash
aws s3api get-object \
  --bucket my-terraform-states \
  --key prod/network/terraform.tfstate \
  --version-id "V2p4gXXXXXXX_LAST_GOOD" local.tfstate
```

3. Push the good state back up forcefully:
```bash
terraform state push local.tfstate
```

---

## 📋 Phase 5: Root Cause Summary & Prevention

### Root Cause
| Factor | Detail |
|--------|--------|
| **What broke** | Terraform State Lock remained stuck |
| **Why it broke** | Jenkins agent lost network connectivity mid-apply / User cancelled a CI job manually |
| **Why it's necessary**| Lock prevents split-brain state corruption from concurrent applies |

### Prevention Checklist
```bash
# 1. Catch pipelines before they hang indefinitely.
# In Jenkinsfile or GH Actions, add a strict timeout:
timeout(time: 30, unit: 'MINUTES') { ... }

# 2. Never allow manual SIGKILL of terraform pipelines.
# Prefer graceful termination.

# 3. ALWAYS ENABLE VERSIONING on the State Bucket (S3/Azure Blob Storage).
# It's the only way to recover from an empty state overwrite.
```

---

## 🧠 Debug Decision Tree (Terraform Pipeline Failures)

```
Pipeline Failed at `plan` or `apply`?
├── Error: "Error acquiring the state lock"
│   ├── Check CI/CD history → Is another job actually running?
│   │   ├── YES → Wait for it to finish.
│   │   └── NO  → It's a stale lock from a crashed job.
│   │             └── Run `terraform force-unlock <ID>`
│
├── Error: "403 Access Denied" on bucket
│   ├── Check CI/CD IAM Role / Azure Managed Identity
│   └── Check Bucket Policies / KMS Key permissions (KMS Decrypt needed)
│
├── Error: "Resource already exists"
│   ├── Resource was created manually outside Terraform (ClickOps).
│   └── Fix: `terraform import <resource.id> <actual-id>` to bring it into state.
│
└── Error: "State is empty or corrupted"
    └── Rollback the `.tfstate` file in S3/Azure Blob using Bucket Versioning.
```
