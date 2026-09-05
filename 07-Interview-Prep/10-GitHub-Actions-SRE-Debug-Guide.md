# 🔥 Production-Grade Debugging Guide

## 🎯 Scenario
- **Cluster/Environment:** Kubernetes (EKS/AKS) running Action Runner Controller (ARC) for self-hosted GitHub Actions
- **Namespace:** `actions-runner-system`
- **Symptom:** Operations reported that the standard CI/CD pipeline—which normally executes in 5 minutes—is suddenly taking 45+ minutes across *all* developer Pull Requests globally. Developers are complaining about excessive queue times.

## 📋 Phase 1: Triage — Confirm the Problem
To get the big picture, we must determine if the delay is happening *inside* the job execution (e.g., slow tests, rate limiting) or *before* the job starts (e.g., infrastructure queuing).
```bash
# 1. Check the GitHub CLI to see where time is being spent
gh run list --limit 5

# 2. Check the capacity of the self-hosted Kubernetes runners
kubectl get pods -n actions-runner-system | grep action-runner
```
**Actual Output:**
```text
STATUS   TITLE        WORKFLOW    BRANCH    TIME
in_prog  Fix API bug  CI/CD-Main  fix-auth  41m 20s

NAME                                          READY   STATUS    RESTARTS   AGE
action-runner-x9k2p-7f5b                      0/1     Pending   0          40m
action-runner-z8m1a-9p2t                      0/1     Pending   0          39m
action-runner-t4c4b-1z8x                      1/1     Running   0          4m
...
action-runner-orphaned-8hx9                   1/1     Running   0          18h  <-- 🚩 RED FLAG
```
*Triage Analysis:* The jobs are not taking 45 minutes to *run*; they are taking 40 minutes to *start* because the pods are stuck in a `Pending` state. Notice the 18-hour-old zombie runner occupying resources.

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis
We need to figure out exactly why the runner pods are pending and why the cluster autoscaler isn't provisioning new nodes to handle the burst.
```bash
# 1. Describe the pending runner pod to check scheduling events
kubectl describe pod action-runner-x9k2p-7f5b -n actions-runner-system

# 2. Check the Cluster Autoscaler logs
kubectl logs -n kube-system deployment/cluster-autoscaler --tail=50 | grep -i "scale-up"
```
**Actual Output:**
```text
Events:
  Type     Reason            Age                 From               Message
  ----     ------            ----                ----               -------
  Warning  FailedScheduling  40m (x12 over 40m)  default-scheduler  0/50 nodes are available: 50 Insufficient cpu, 50 Insufficient memory.

[...]
# Autoscaler Logs:
I0906 08:12:22.102345 1 scale_up.go:420] Pod action-runner-x9k2p-7f5b is unschedulable
W0906 08:12:22.105432 1 scale_up.go:452] max node group size reached: 50/50 nodes  <-- 🚩 RED FLAG
```
*Deep Dive Analysis:* The Action Runner Controller created the pods, but the Kubernetes Cluster Autoscaler has hit its hard-capped limit of 50 nodes. The cluster is completely saturated due to a buildup of "zombie" non-ephemeral runners that did not clean themselves up after past jobs.

## 📋 Phase 3: The Fix
### Option A (The Fastest/Inline Fix)
Immediately purge the stuck, orphaned runner pods from the previous day to free up CPU/Memory and allow the queue to unblock.
```bash
kubectl delete pods -n actions-runner-system -l runner-state=idle --field-selector status.phase=Running
```

### Option B (The Proper/Manifest Edit)
Modify the Action Runner Controller deployment to ensure runners are strictly ephemeral (they destroy themselves after 1 job), and increase the autoscaler max-size limit slightly to handle the immediate backlog.
```bash
# 1. Patch the RunnerDeployment to enforce ephemeral jobs
kubectl patch runnerdeployment my-runner -n actions-runner-system --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/ephemeral", "value": true}]'

# 2. Scale the NodePool max size in Terraform or cloud CLI (Emergency Azure Example)
az aks nodepool update --resource-group my-rg --cluster-name my-aks --name runnerpool --update-cluster-autoscaler --max-count 75
```

### Option C (The Emergency Rollback/Mitigation)
If the cluster is entirely unresponsive, emergency-route critical CI/CD traffic back to GitHub's hosted SaaS runners so developers can merge hotfixes.
```bash
# Inside .github/workflows/main.yml
# Change this:
# runs-on: [self-hosted, linux, x64]
# To this:
sed -i 's/runs-on: \[self-hosted, linux, x64\]/runs-on: ubuntu-latest/g' .github/workflows/main.yml
git commit -am "hotfix: temporal shift to gh-hosted runners" && git push
```

## 📋 Phase 5: Verify the Fix
Monitor the Action namespaces and confirm a massive wave of `ContainerCreating` events as the backlog floods into the newly freed resources.
```bash
kubectl get pods -n actions-runner-system -w
```
**Actual Output:**
```text
NAME                                READY   STATUS              RESTARTS   AGE
action-runner-x9k2p-7f5b            0/1     ContainerCreating   0          41m
action-runner-x9k2p-7f5b            1/1     Running             0          41m  <-- FIRED
action-runner-z8m1a-9p2t            0/1     ContainerCreating   0          40m
action-runner-z8m1a-9p2t            1/1     Running             0          40m  <-- FIRED
```
All pull requests in GitHub will instantly transition from "Queued" to "In Progress".

## 📋 Phase 6: Root Cause Summary & Prevention

| Metric | Details |
| :--- | :--- |
| **What Broke** | CI/CD pipelines queued for 40+ minutes before starting. |
| **Why it Broke** | Non-ephemeral runner pods became zombified, saturating the cluster's Maximum Node limit (50). New pipeline pods were stuck in `Pending`. |
| **Fail State** | `FailedScheduling` / `max node group size reached` |

**Prevention Checklist:**
- [x] **Enforce Ephemeral Runners:** Ensure `ephemeral: true` is strictly set in the ARC manifest.
- [x] **Datadog/Prometheus Queue Alerts:** Configure alerts to fire if Webhook Queue Time > 5 minutes.
  ```bash
  # Example PromQL alert trigger:
  github_actions_runner_queue_duration_seconds > 300
  ```
- [x] **Pod Garbage Collection:** Configure a scheduled CronJob to purge runners older than 2 hours.
  ```bash
  kubectl create cronjob runner-cleanup --image=bitnami/kubectl --schedule="0 * * * *" -- \
  delete pods -n actions-runner-system --field-selector status.phase=Running -l age>2h
  ```

## 🧠 Debug Decision Tree
```text
[Pipeline Takes 45 Minutes]
 ├── Check GitHub Actions UI 
 │
 ├── Job is inside "In Progress" for 45 mins?
 │    ├── YES -> Check Step Logs.
 │    │    ├── NPM/Docker Pull failing? -> Registry Rate Limit (429).
 │    │    └── Hanging on Script? -> Database deadlock or Timeout.
 │    │
 │    └── NO -> It's stuck in "Queued" for 40 mins.
 │
 └── Check Kubernetes Runner Namespace (`kubectl get pods`)
      ├── Pods are Running? -> Check ARC Controller logs for auth failures.
      └── Pods are Pending? -> Resources exhausted.
           └── `kubectl describe pod` -> FailedScheduling
                └── Check `cluster-autoscaler` logs
                     └── Limit reached? -> Manually purge zombies & adjust auto-scaler quotas.
```

## ⚡ Quick Reference Commands
```bash
# 1. View running vs queued GitHub actions
gh run list

# 2. View all runner pods and filter by Pending status
kubectl get pods -n actions-runner-system --field-selector status.phase=Pending

# 3. Diagnose the specific pending reason
kubectl describe pod <pod-name> -n actions-runner-system | tail -n 15

# 4. View Cluster Autoscaler behavior (kube-system)
kubectl logs -n kube-system deployment/cluster-autoscaler | grep "max node group"

# 5. Emergency mass-delete of zombie pods (e.g. idle runners)
kubectl delete pods -n actions-runner-system -l runner-state=idle

# 6. Monitor recovery dynamically
kubectl get pods -n actions-runner-system -w
```
