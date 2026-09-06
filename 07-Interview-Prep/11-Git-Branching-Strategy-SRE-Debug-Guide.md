# 🔥 Production-Grade Debugging Guide

## 🎯 Scenario
- **Cluster/Environment:** Kubernetes GitOps Repository (ArgoCD/Flux) managed via GitHub.
- **Namespace:** `argocd-system`
- **Symptom:** A developer force-merged the `feature-example-ingress` branch into `master` containing malformed Kubernetes configurations, and the feature branch was immediately deleted. Because your cluster uses GitOps, ArgoCD immediately attempted to sync the broken `master` branch, failing catastrophically and halting all production infrastructure updates.

## 📋 Phase 1: Triage — Confirm the Problem
To get the big picture, we must immediately verify the state of the Git history on the `master` branch and confirm what the GitOps controller is seeing.
```bash
# 1. Fetch the latest history from the remote repository
git fetch origin

# 2. View the recent commit history to identify the bad merge
git log --oneline --graph -n 5

# 3. Check the ArgoCD sync status in the cluster
argocd app get cluster-infrastructure
```
**Actual Output:**
```text
* d8b5f3a (HEAD -> master, origin/master) Merge pull request #145 from imranshs08/feature-example-ingress  <-- 🚩 RED FLAG
|\  
| * a1b2c3d (deleted: feature-example-ingress) Updated ingress YAML (broken syntax)
|/  
* 9f7d2e1 Last known good stable production state

# ArgoCD Status:
Sync Status: OutOfSync
Health Status: Degraded
Conditions:    ComparisonError: error validating data: ValidationError(Ingress.spec): unknown field "rulse" in io.k8s.api.networking.v1.IngressSpec
```
*Triage Analysis:* The `feature-example-ingress` branch was merged into `master` and subsequently deleted. The merge introduced a typo (`rulse` instead of `rules`) in a core Kubernetes Ingress yaml file, completely breaking the GitOps deployment pipeline.

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis
We need to pinpoint exactly what was changed in the massive merge commit to understand the blast radius before we execute a reversion.
```bash
# 1. Inspect the exact diff introduced by the merge commit relative to the stable parent
# -m 1 specifies the first parent (the main branch)
git diff d8b5f3a^1 d8b5f3a

# 2. Check Git Reflog in case someone did a hard reset and we need to recover the lost branch
git reflog show
```
**Actual Output:**
```diff
diff --git a/k8s-manifests/production-ingress.yaml b/k8s-manifests/production-ingress.yaml
index 8e45f9a..c3a2b1f 100644
--- a/k8s-manifests/production-ingress.yaml
+++ b/k8s-manifests/production-ingress.yaml
@@ -9,7 +9,7 @@ metadata:
 spec:
   ingressClassName: nginx
-  rules:
+  rulse:  <-- 🚩 RED FLAG
   - host: api.production.internal
```
*Deep Dive Analysis:* The diff confirms a critical syntax error in `production-ingress.yaml` was directly introduced in the merge commit `d8b5f3a`. 

## 📋 Phase 3: The Fix
### Option A (The Fastest/Inline Fix)
The safest and most auditable way to undo a broken merge in a shared remote track is to `revert` the merge commit safely, indicating which parent branch to keep.
```bash
# Revert the merge commit, strictly using parent 1 (the original master baseline)
git revert -m 1 d8b5f3a

# Push the reverted state back to GitHub immediately
git push origin master
```

### Option B (The Proper/Manifest Edit)
If the feature code is 99% correct and you just need to fix the typo quickly without entirely reverting the feature team's work.
```bash
# 1. Create a hotfix branch off the broken master
git checkout -b hotfix-ingress-typo master

# 2. Fix the file inline
sed -i 's/rulse/rules/g' k8s-manifests/production-ingress.yaml

# 3. Commit and merge the fix natively
git commit -am "fix(ingress): corrected yaml syntax bypass"
git push origin hotfix-ingress-typo
gh pr create --fill && gh pr merge --auto --squash
```

### Option C (The Emergency Rollback/Mitigation)
If the bad code was already pulled by GitOps and ArgoCD is currently deleting cluster resources erroneously (Cascade Deletion), hard-stop ArgoCD sync immediately.
```bash
# Suspend the continuous deployment engine immediately to stop the cluster from destroying resources
kubectl patch application cluster-infrastructure -n argocd --type='json' -p='[{"op": "add", "path": "/spec/syncPolicy/automated", "value": null}]'
```

## 📋 Phase 5: Verify the Fix
Verify that the `master` branch head is restored to a valid state and the GitOps controller successfully syncs.
```bash
# 1. Confirm the revert commit is at the top of the HEAD
git log --oneline -n 2

# 2. Force ArgoCD to check the repo and sync the repaired manifest
argocd app sync cluster-infrastructure
```
**Actual Output:**
```text
6c4e1f9 (HEAD -> master, origin/master) Revert "Merge pull request #145 from imranshs08/feature-example-ingress"
d8b5f3a Merge pull request #145 from imranshs08/feature-example-ingress

# ArgoCD Sync Output:
Phase:              Succeeded  <-- FIRED
Resource Status:    Synced
Health:             Healthy
```

## 📋 Phase 6: Root Cause Summary & Prevention

| Metric | Details |
| :--- | :--- |
| **What Broke** | Kubernetes deployments halted because GitOps hit a YAML parsing error. |
| **Why it Broke** | A feature branch with untested code was merged into `master` and the branch was deleted. This bypassed testing, merging invalid Kubernetes syntax (`rulse` instead of `rules`). |
| **Fail State** | `ValidationError` / `OutOfSync` |

**Prevention Checklist:**
- [x] **Enforce GitHub Branch Protection (Critical):**
  ```bash
  gh api -X PUT /repos/imranshs08/kubernetes-project/branches/master/protection \
    -f required_status_checks[strict]=true \
    -f enforce_admins=true \
    -f required_pull_request_reviews[required_approving_review_count]=1
  ```
- [x] **Implement CI/CD Linting (Pre-Merge Check):** Add `kubeval` or `kube-linter` to GitHub Actions on pull requests *before* the merge is allowed.
- [x] **Auto-Delete Branches:** Ensure "Automatically delete head branches" is standardized in Repository Settings, but only *after* CI passes.

## 🧠 Debug Decision Tree
```text
[Bad Code Merged to Master]
 ├── Check Branch History (`git log --graph`) 
 │
 ├── Was it a standard commit or a Merge Commit?
 │    ├── Merge Commit -> Use `git revert -m 1 <commit-hash>`
 │    │    ├── Did it revert cleanly?
 │    │    │    ├── YES -> Push `master` & trigger Sync.
 │    │    │    └── NO -> Resolve revert conflicts manually.
 │    │
 │    └── Standard Commit -> Use standard `git revert <commit-hash>`
 │
 └── Check Kubernetes State
      ├── ArgoCD attempting destructive Sync? -> Suspend Application Auto-Sync.
      └── ArgoCD stuck OutOfSync? -> Wait for git push and manually run `argocd app sync`.
```

## ⚡ Quick Reference Commands
```bash
# 1. View branching history and find the offending merge commit
git log --oneline --graph --decorate -n 10

# 2. View the reflog to find recently deleted or moved branch pointers
git reflog

# 3. View the delta/diff of a merge commit against its parent
git diff <merge-commit-hash>^1 <merge-commit-hash>

# 4. Safely revert an entire merged feature branch
git revert -m 1 <merge-commit-hash>

# 5. Bring back a deleted branch if you still need its code
git checkout -b feature-example-ingress <commit-hash-before-merge>

# 6. Apply a fast-forward GitOps sync manually after fixing Master
argocd app sync <app-name> --force
```
