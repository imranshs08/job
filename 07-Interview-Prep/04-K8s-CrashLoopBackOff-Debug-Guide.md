# 🔥 Production-Grade Kubernetes Debugging Guide

> **Template Prompt:**
> *"My Kubernetes cluster has the following issue: [describe]. Cluster: [EKS/AKS/Kind]. Version: [version]. Error: [paste error]. Provide a step-by-step debugging approach with kubectl commands."*

---

## 🎯 Scenario: Nginx Pods Stuck in CrashLoopBackOff — OOMKilled

- **Cluster:** Amazon EKS
- **Version:** 1.28
- **Namespace:** `production`
- **Symptom:** Nginx deployment pods keep restarting

---

## 📋 Phase 1: Triage — Confirm the Problem

### Step 1.1 — Get the Big Picture

```bash
kubectl get pods -n production -o wide
```

**Actual Output:**
```
NAME                               READY   STATUS             RESTARTS   AGE    IP              NODE
nginx-deployment-6d9f4b7c8-4xkpz   0/1     CrashLoopBackOff   8          18m    10.0.12.45      ip-10-0-1-101.ec2.internal
nginx-deployment-6d9f4b7c8-9wlmn   0/1     CrashLoopBackOff   7          18m    10.0.14.22      ip-10-0-1-204.ec2.internal
nginx-deployment-6d9f4b7c8-k2rvp   0/1     OOMKilled          12         18m    10.0.12.67      ip-10-0-1-101.ec2.internal
```

> 🔴 **Red Flag:** `RESTARTS: 8, 7, 12` + `OOMKilled` — containers are running out of memory.

---

### Step 1.2 — Describe the Failing Pod

```bash
kubectl describe pod nginx-deployment-6d9f4b7c8-4xkpz -n production
```

**Actual Output (key sections):**
```
Name:         nginx-deployment-6d9f4b7c8-4xkpz
Namespace:    production
Node:         ip-10-0-1-101.ec2.internal/10.0.1.101
...
Status:       Running
Containers:
  nginx:
    Image:          nginx:1.25-alpine
    Limits:
      memory:       64Mi        ← ⚠️ TOO LOW
    Requests:
      memory:       32Mi
    Last State:     Terminated
      Reason:       OOMKilled   ← 💥 ROOT CAUSE
      Exit Code:    137
      Started:      Thu, 04 Sep 2026 14:32:01 +0530
      Finished:     Thu, 04 Sep 2026 14:32:45 +0530

Events:
  Type     Reason     Age                  From               Message
  ----     ------     ----                 ----               -------
  Normal   Scheduled  19m                  default-scheduler  Successfully assigned production/nginx-deployment-6d9f4b7c8-4xkpz to ip-10-0-1-101.ec2.internal
  Normal   Pulled     19m                  kubelet            Container image "nginx:1.25-alpine" already present on machine
  Normal   Created    19m (x4 over 19m)    kubelet            Created container nginx
  Normal   Started    19m (x4 over 19m)    kubelet            Started container nginx
  Warning  BackOff    2m (x18 over 17m)    kubelet            Back-off restarting failed container
  Warning  OOMKilling 3m (x4 over 19m)     kernel             Out of memory: Kill process 14721 (nginx) score 910 or sacrifice child
```

> 🔴 **Confirmed:** Memory limit set to `64Mi`. Nginx under load requires `~150–256Mi`. Exit code `137` = killed by OS (SIGKILL from OOM killer.

---

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis

### Step 2.1 — Check Container Logs

```bash
# Current logs
kubectl logs nginx-deployment-6d9f4b7c8-4xkpz -n production

# Previous (crashed) container logs — MOST IMPORTANT
kubectl logs nginx-deployment-6d9f4b7c8-4xkpz -n production --previous
```

**Actual Output (`--previous`):**
```
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/09/04 08:47:12 [notice] 1#1: start worker processes
2026/09/04 08:47:12 [notice] 1#1: start worker process 31
...
Killed                             ← process killed by Linux OOM killer
```

---

### Step 2.2 — Check Node-Level Pod Metrics

```bash
kubectl top pods -n production
```

**Actual Output:**
```
NAME                               CPU(cores)   MEMORY(bytes)
nginx-deployment-6d9f4b7c8-4xkpz   42m          61Mi/64Mi    ← 95% of limit!
nginx-deployment-6d9f4b7c8-9wlmn   38m          63Mi/64Mi    ← AT LIMIT
nginx-deployment-6d9f4b7c8-k2rvp   0m           0Mi          ← just crashed
```

```bash
kubectl top nodes
```

**Actual Output:**
```
NAME                         CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
ip-10-0-1-101.ec2.internal   312m         16%    2847Mi          74%
ip-10-0-1-204.ec2.internal   287m         15%    2901Mi          76%
```

> 🟡 **Nodes have plenty of memory (74-76%).** The issue is the pod's memory **limit is too low**, not the node.

---

### Step 2.3 — Inspect the Deployment Spec

```bash
kubectl get deployment nginx-deployment -n production -o yaml | grep -A 15 resources
```

**Actual Output:**
```yaml
        resources:
          requests:
            memory: "32Mi"
            cpu: "100m"
          limits:
            memory: "64Mi"      ← 💥 THE PROBLEM
            cpu: "500m"
```

---

## 📋 Phase 3: Check the Deployment Rollout History

```bash
kubectl rollout history deployment/nginx-deployment -n production
```

**Actual Output:**
```
REVISION  CHANGE-CAUSE
1         kubectl apply --filename=nginx-deployment.yaml --record=true
2         kubectl set image deployment/nginx-deployment nginx=nginx:1.25-alpine --record=true
3         kubectl set resources deployment/nginx-deployment -c nginx --limits=memory=64Mi --record=true
```

> 🔴 **Revision 3 introduced the memory limit reduction** — this is the breaking change.

---

## 📋 Phase 4: The Fix

### Option A — Patch Memory Limit Inline (Fastest)

```bash
kubectl patch deployment nginx-deployment -n production \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "256Mi"},
       {"op": "replace", "path": "/spec/template/spec/containers/0/resources/requests/memory", "value": "128Mi"}]'
```

**Actual Output:**
```
deployment.apps/nginx-deployment patched
```

---

### Option B — Edit Deployment Directly

```bash
kubectl edit deployment nginx-deployment -n production
```

Change in the editor:
```yaml
# BEFORE:
resources:
  requests:
    memory: "32Mi"
  limits:
    memory: "64Mi"

# AFTER:
resources:
  requests:
    memory: "128Mi"
  limits:
    memory: "256Mi"
```

---

### Option C — Rollback to Last Good Revision (Emergency)

```bash
# Roll back to revision 2 (before the bad memory limit was set)
kubectl rollout undo deployment/nginx-deployment -n production --to-revision=2
```

**Actual Output:**
```
deployment.apps/nginx-deployment rolled back
```

---

## 📋 Phase 5: Verify the Fix

### Step 5.1 — Watch Rollout

```bash
kubectl rollout status deployment/nginx-deployment -n production
```

**Actual Output:**
```
Waiting for deployment "nginx-deployment" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 2 of 3 updated replicas are available...
deployment "nginx-deployment" successfully rolled out
```

---

### Step 5.2 — Confirm Pods are Stable

```bash
kubectl get pods -n production -w
```

**Actual Output:**
```
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-7b9d5c6f4-2rknp   1/1     Running   0          2m
nginx-deployment-7b9d5c6f4-8jlqv   1/1     Running   0          90s
nginx-deployment-7b9d5c6f4-xp4mn   1/1     Running   0          65s
```

> ✅ **RESTARTS = 0.** All pods running. Fix confirmed.

---

### Step 5.3 — Confirm Memory Usage Within New Limits

```bash
kubectl top pods -n production
```

**Actual Output:**
```
NAME                               CPU(cores)   MEMORY(bytes)
nginx-deployment-7b9d5c6f4-2rknp   35m          88Mi/256Mi    ← 34% — healthy
nginx-deployment-7b9d5c6f4-8jlqv   31m          91Mi/256Mi    ← 35% — healthy
nginx-deployment-7b9d5c6f4-xp4mn   33m          85Mi/256Mi    ← 33% — healthy
```

---

## 📋 Phase 6: Root Cause Summary & Prevention

### Root Cause
| Factor | Detail |
|--------|--------|
| **What broke** | Memory limit set to `64Mi` in Revision 3 |
| **Why it broke** | Nginx worker + lua modules require `~150Mi` at load |
| **Exit code** | `137` (SIGKILL — OOM kill, not application crash) |
| **Why it looped** | Kubelet exponential backoff restarts on OOMKilled containers |

### Prevention Checklist
```bash
# 1. Always check VPA recommendations before setting limits
kubectl describe vpa nginx-vpa -n production

# 2. Set limits at 2x of observed peak, not arbitrary values
kubectl top pods -n production --sort-by=memory

# 3. Add OOMKilled alerting via Prometheus
# Alert rule:
# kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} > 0

# 4. Use resource quotas at namespace level, not per-pod guesswork
kubectl describe resourcequota -n production
```

### Request/Limit Golden Ratios for Common Workloads
| Workload | Request Memory | Limit Memory |
|----------|---------------|--------------|
| Nginx (low traffic) | 64Mi | 128Mi |
| Nginx (production) | 128Mi | 256Mi |
| Node.js API | 256Mi | 512Mi |
| Java Spring Boot | 512Mi | 1Gi |
| Python Flask | 128Mi | 256Mi |

---

## 🧠 Debug Decision Tree

```
Pod not Ready?
├── STATUS = CrashLoopBackOff
│   ├── kubectl logs <pod> --previous          ← check last crash output
│   ├── kubectl describe pod <pod>             ← check Events + Exit Code
│   │   ├── Exit Code 137 → OOMKilled          ← increase memory limit
│   │   ├── Exit Code 1   → App error          ← fix application config
│   │   └── Exit Code 128 → Missing binary     ← fix image/entrypoint
│   └── kubectl rollout history deployment/<name>  ← find the breaking change
│
├── STATUS = Pending
│   ├── kubectl describe pod → "Insufficient memory/cpu"  ← scale nodes
│   └── kubectl describe pod → "Unschedulable"            ← check taints/affinity
│
├── STATUS = ImagePullBackOff
│   ├── Wrong image tag → fix deployment image
│   └── Private registry → check imagePullSecrets
│
└── STATUS = Running but not Ready
    ├── kubectl describe pod → check Readiness probe
    └── kubectl logs <pod>  → check app startup error
```

---

## ⚡ Quick Reference Commands

```bash
# All-in-one pod debug
kubectl get pods -n <ns> -o wide
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> --previous
kubectl top pods -n <ns>

# Deployment inspection
kubectl rollout history deployment/<name> -n <ns>
kubectl rollout undo deployment/<name> -n <ns>
kubectl get deployment <name> -n <ns> -o yaml | grep -A 10 resources

# Node health
kubectl top nodes
kubectl describe node <node-name> | grep -A 10 "Allocated resources"

# Events (sorted, cluster-wide)
kubectl get events -n <ns> --sort-by='.lastTimestamp' | tail -20
```
