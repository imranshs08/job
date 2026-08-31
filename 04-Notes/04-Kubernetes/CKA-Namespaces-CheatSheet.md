# CKA Cheat Sheet: Kubernetes Namespaces

> **Scope**: Core Concepts (Isolation)  
> **Tracker Date**: Aug 31, 2026

Namespaces provide a mechanism for isolating groups of resources within a single Kubernetes cluster. They are like "virtual clusters" inside the physical cluster.

---

## 1. Default Namespaces

When you spin up a cluster, Kubernetes creates 4 initial namespaces:
1. `default`: The default active namespace where user objects go if no namespace is specified.
2. `kube-system`: For objects created by the Kubernetes system (CoreDNS, kube-proxy, control plane pods).
3. `kube-public`: Globally readable workspace, primarily used for cluster bootstrapping/discovery info.
4. `kube-node-lease`: Holds Lease objects associated with each node for node heartbeat monitoring.

---

## 2. ⚡ Imperative Commands (CKA Speed Strategy)

```bash
# Create a namespace
kubectl create namespace web-prod
# (alias: kubectl create ns web-prod)

# List all namespaces
kubectl get ns

# Launch a pod in a specific namespace
kubectl run redis --image=redis -n web-prod

# Get pods from ALL namespaces
kubectl get pods --all-namespaces
# (alias: kubectl get pods -A)
```

---

## 3. Changing Contexts (Exam Time-Saver)

In the CKA, you'll be switching between namespaces constantly. Passing `-n <namespace>` repeatedly wastes time and causes typos. 

Change your default context:
```bash
# Set default namespace to 'web-prod' for current context
kubectl config set-context --current --namespace=web-prod

# Verify your context
kubectl config view --minify | grep namespace:
```

---

## 4. Resource Quotas

Namespaces are primarily used for Resource Quotas to restrict team usage.
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: dev-team
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "10"
```
*If a pod violates the quota, the creation will be rejected with an `HTTP 403 Forbidden` error.*

---

## 5. Cross-Namespace Communication

- Namespaces do **not** provide network isolation by default. A pod in the `dev` namespace can ping a pod in the `prod` namespace!
- To restrict cross-namespace traffic, you must explicitly implement **NetworkPolicies**.
- To communicate with a service in another namespace, use the FQDN: `http://service-name.target-namespace.svc.cluster.local`
