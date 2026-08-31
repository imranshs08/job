# CKA Cheat Sheet: ReplicaSets

> **Scope**: Core Concepts (Workloads / Self-Healing)
> **Tracker Date**: Aug 25 - Aug 26, 2026

A ReplicaSet's purpose is to maintain a stable set of replica Pods running at any given time. As such, it is often used to guarantee the availability of a specified number of identical Pods.

---

## 1. How ReplicaSets Work (The Selector Mechanism)

ReplicaSets monitor Pods using **Selectors** (specifically `matchLabels`). 
If a Pod goes down, the ReplicaSet brings up a new one to meet the desired `replicas` count.
If there are *too many* Pods matching the label (e.g., someone created a manual pod with the same label), the ReplicaSet will terminate the exact number of extra Pods to reach the desired state.

⚠️ *Note: You almost never deploy ReplicaSets directly in production. You deploy **Deployments**, which manage ReplicaSets automatically (allowing for rollouts and rollbacks).*

---

## 2. ⚡ Imperative Commands (CKA Speed Strategy)

There is **no** direct imperative command to create a ReplicaSet (like `kubectl create replicaset`).
In the exam, you have two options:
1. Create a Deployment, then extract and modify its YAML if a strict ReplicaSet is required.
2. Quickly write a YAML file from memory.

**Scaling a ReplicaSet Imperatively:**
```bash
kubectl scale replicaset my-rs --replicas=5
# (alias: kubectl scale rs my-rs --replicas=5)
```

---

## 3. Minimal ReplicaSet YAML Structure

Since there's no imperative generator, memorize this structure, or copy it from the Kubernetes docs during the exam:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      tier: frontend   # 1. This MUST match the Pod template labels below
  template:
    metadata:
      labels:
        tier: frontend # 2. Labels applied to the generated Pods
    spec:
      containers:
      - name: nginx
        image: nginx:latest
```

---

## 4. Typical Exam Task: Fixing a Broken ReplicaSet

**Scenario:** The exam asks why a ReplicaSet isn't bringing up pods, or why the pods are instantly orphaned.

**The Fix:** 
Check if the `selector.matchLabels` in the ReplicaSet spec matches the `labels` in the Pod `template.metadata`. If they do not match, the ReplicaSet will fail to adopt the created pods, and will either stop creating them or endlessly create orphaned pods depending on the Kubernetes version.

```bash
# Easiest way to edit a broken ReplicaSet on the fly:
kubectl edit rs <replicaset-name>
```
