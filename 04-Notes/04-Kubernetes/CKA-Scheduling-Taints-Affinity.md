# CKA Cheat Sheet: Scheduling (Taints, Tolerations, Affinity)

> **Scope**: Workloads & Scheduling (15%)  
> **Tracker Link**: [README.md](README.md)

Kubernetes scheduling is about ensuring Pods land on the exactly correct Nodes.

---

## 1. Taints and Tolerations
* **Taints** are applied to **Nodes**. They repel Pods. (Analogy: Bug spray)
* **Tolerations** are applied to **Pods**. They allow a pod to ignore a taint. (Analogy: Bug immunity)

**Important:** Tolerations do *not* guarantee a pod will land on a tainted node. They just *allow* it. The pod could still land on a perfectly clean, untainted node elsewhere.

### Imperative Commands:
```bash
# Apply a taint to node01 (Format: key=value:Effect)
kubectl taint nodes node01 color=blue:NoSchedule

# Remove a taint (add a minus sign at the end)
kubectl taint nodes node01 color=blue:NoSchedule-
```
*Effects: `NoSchedule` (repels new pods), `PreferNoSchedule` (soft repel), `NoExecute` (evicts currently running pods).*

### Pod Toleration YAML:
```yaml
      tolerations:
      - key: "color"
        operator: "Equal"
        value: "blue"
        effect: "NoSchedule"
```

---

## 2. Node Selectors
The simplest way to schedule a pod to a specific node.
```bash
# Label a node first
kubectl label nodes node02 disk=ssd
```
```yaml
    spec:
      nodeSelector:
        disk: ssd
```
*Drawback: Node selectors are strictly binary. If no node has `disk=ssd`, the pod stays Pending forever.*

---

## 3. Node Affinity
The advanced, highly expressive version of NodeSelectors. It allows logical operators (In, NotIn, Exists) and soft/hard rules.

1. **requiredDuringSchedulingIgnoredDuringExecution**: Hard rule. Must be met.
2. **preferredDuringSchedulingIgnoredDuringExecution**: Soft rule. Tries to meet it, but will schedule elsewhere if it can't.

```yaml
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: disk
                operator: In
                values:
                - ssd
                - nvme
```

---

## 4. Manual Scheduling (No Scheduler!)
If the `kube-scheduler` component is completely dead in your cluster, you can bypass it and manually force a Pod onto a node by specifying the `nodeName` in the pod spec.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: manual-pod
spec:
  nodeName: node01   # Bypasses the scheduler entirely!
  containers:
  - name: nginx
    image: nginx
```
