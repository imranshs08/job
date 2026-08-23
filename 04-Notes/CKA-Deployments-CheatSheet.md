# ☸️ CKA Notes: Kubernetes Deployments

> **Objective:** Understand how Deployments abstract and manage ReplicaSets, enabling rolling updates, rollbacks, and zero-downtime scaling.

---

## 🧠 Core Architecture
A **Deployment** is a higher-level controller that manages **ReplicaSets**, which in turn manage **Pods**.
- You should *almost never* create ReplicaSets directly in production. Always use Deployments.
- If you update a Deployment's template (e.g., change the image version), it spins up a *new* ReplicaSet and orchestrates a graceful transition (Rolling Update) from the old ReplicaSet to the new one.

---

## ⚡ Imperative Commands (The Fast Way)

In the CKA exam, speed is everything. DO NOT write deployment YAML from scratch!

```bash
# Generate a deployment quickly (creates the YAML template for you)
kubectl create deployment my-dep --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Directly scale a deployment imperatively
kubectl scale deployment my-dep --replicas=5

# Change the image of a live deployment (Triggers a Rolling Update!)
kubectl set image deployment/my-dep nginx=nginx:1.16.1 --record
```

---

## 🔄 Rolling Updates & Rollbacks (Crucial for CKA)

When a deployment is modified, it creates a new "Revision". You can inspect these revisions and instantly roll back if you break production.

```bash
# Check the status of a rollout
kubectl rollout status deployment/my-dep

# View the deployment history (revisions)
kubectl rollout history deployment/my-dep

# 🚨 OH NO, PRODUCTION BROKE! Rollback to the previous version instantly:
kubectl rollout undo deployment/my-dep

# Rollback to a specific historical revision:
kubectl rollout undo deployment/my-dep --to-revision=2
```

---

## 📝 Declarative YAML Skeleton

Notice that the `spec` structure is almost *identical* to a ReplicaSet! The only difference is `kind: Deployment`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  labels:
    app: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:         # <--- POD DEFINITION STARTS HERE
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        ports:
        - containerPort: 80
```

---

## 🎯 Pro-Tips for the Exam
1. **Always use `--record`**: If a question asks you to update an image, add `--record` so the exact command shows up in the `rollout history`.
2. **Watch your labels**: If your Deployment's `selector` doesn't strictly match your Pod `template` labels, it will crash.
3. **Deployment vs Pod**: Deployments only trigger rollout updates if the *Pod Template* changes (e.g., labels, environment variables, image). Scaling replicas does *not* trigger a rollout revision.
