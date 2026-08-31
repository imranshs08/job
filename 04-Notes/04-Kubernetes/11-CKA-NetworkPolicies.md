# CKA Cheat Sheet: Network Policies

> **Scope**: Networking / Security  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

By default in Kubernetes, **all pods can talk to all pods** across all namespaces. It is a completely open/flat network. Network Policies act as the "firewall rules" for Kubernetes to restrict this lateral movement.

---

## 1. Network Policy Concepts

- Network Policies require a CNI plugin that supports them (e.g., Calico, Cilium, Weave). If you use Flannel, creating a NetworkPolicy does absolutely nothing!
- **Ingress**: Incoming traffic *to* the pod.
- **Egress**: Outgoing traffic *from* the pod.
- **Default Deny Strategy**: The moment a Network Policy selects a pod using `podSelector`, that pod instantly rejects ALL traffic that isn't explicitly allowed by the policy (it becomes isolated).

---

## 2. Reading the YAML

Always pull this structure from the K8s Docs during the exam. (Search "Network Policies").

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-network-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db           # 1. This isolates the DB pods!
  policyTypes:
    - Ingress            # We are writing Ingress rules
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              project: myproject   # Allow traffic if it comes from this namespace
        - podSelector:
            matchLabels:
              role: frontend       # AND allow traffic if it comes from frontend pods
      ports:
        - protocol: TCP
          port: 6379               # Only on port 6379 (Redis)
```

---

## 3. The "Default Deny All" Policy

It is a best practice (and common exam task) to lock down an entire namespace so nothing can communicate by default.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: secure-ns
spec:
  podSelector: {}      # An empty selector selects ALL pods in the namespace
  policyTypes:
  - Ingress
  # Notice there is no 'ingress:' rule block. This means block everything.
```

## 4. The "Allow All Ingress" Policy (The undo button)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-ingress
  namespace: secure-ns
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - {}                 # An empty rule block means allow everything.
```
