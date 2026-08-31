# CKA Cheat Sheet: StatefulSets & DaemonSets

> **Scope**: Advanced Workloads  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

---

## 1. StatefulSets

StatefulSets are used for applications that require unique network identifiers, stable persistent storage, and ordered, graceful deployment and scaling (e.g., Databases like MySQL, Cassandra, Elasticsearch).

### Key Characteristics vs Deployments:
- **Sticky Identity:** Pods are named sequentially (e.g., `mysql-0`, `mysql-1`, `mysql-2`) instead of having random hashes (`nginx-84d5f-xyz`).
- **Ordered Operations:** Pods are created, updated, and deleted in strict order (0, then 1, then 2). 
- **VolumeClaimTemplates:** This is the killer feature. Instead of multiple pods sharing the same PVC (which would corrupt a database), a StatefulSet uses a `volumeClaimTemplate`. As each Pod is spun up, K8s creates a brand new unique PVC (and dynamically provisions a PV) explicitly for that specific Pod.

### The Headless Service Requirement
StatefulSets require a "Headless Service" (a service with `clusterIP: None`). This is because we don't want a load balancer hitting a random database replica; we need a direct DNS entry to reach a specific pod (like hitting the master node only).
- DNS Format: `pod-name.headless-service-name.namespace.svc.cluster.local`

---

## 2. DaemonSets

A DaemonSet ensures that a copy of a specified Pod runs on **every single Node** (or a subset of nodes based on taints/labels) in the cluster.

### Common Use Cases:
- **Log Collection:** running `fluentd` or `logstash` on every node.
- **Monitoring:** running `Prometheus Node Exporter` or `Datadog agent` on every node.
- **Networking:** running `kube-proxy` or the `calico-node` CNI plugin.

### Modifying from a Deployment (Exam Tip!)
There is **no imperative command** to create a DaemonSet! 
In the CKA exam, the fastest way to create a DaemonSet is:
1. `kubectl create deployment fluentd --image=fluentd --dry-run=client -o yaml > daemon.yaml`
2. Open `daemon.yaml`
3. Change `kind: Deployment` to `kind: DaemonSet`
4. Delete the `replicas: 1` line (DaemonSets don't use replicas; they just run 1 per node).
5. Delete the `strategy:` block.
6. `kubectl apply -f daemon.yaml`

---

## 3. Node Affinity vs Taints regarding DaemonSets
By default, a DaemonSet runs on *all* nodes (except the Master/Control Plane nodes, due to their NoSchedule taint). 
If you only want your DaemonSet to run on Nodes equipped with GPUs, you would add a `nodeSelector` or `nodeAffinity` rule to the pod template inside the DaemonSet spec.
