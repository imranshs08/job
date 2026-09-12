# 📘 DaemonSets

## 🎯 The "Why" (Core Concept)
- **Concept:** A `DaemonSet` guarantees that exactly **one copy** of a specific Pod runs on **every single Node** in the cluster (or a specific subset of nodes if filtered by NodeSelectors).
- **The Analogy:** Think of a Hotel Security system. A `Deployment` is like hiring 5 random security guards—they might all hang out in the lobby, leaving the upper floors unprotected. A `DaemonSet` guarantees you post exactly **1 guard on every single floor**, automatically adding a new guard the second a new floor is built.
- **Catastrophic Problem Solved:** It prevents **Infrastructure Blind Spots**. If you deploy log-forwarders or networking agents using standard Deployments, the scheduler might place them all on a single node. DaemonSets ensure critical cluster-level infrastructure exists natively across the entire topology.

## ⚙️ Architecture & Under the Hood
- **Primary Use Cases:** `kube-proxy` (networking rule translation), **Calico/Weave** (CNI networking agents), and **Fluentd/Datadog** (monitoring/logging agents) are universally deployed via DaemonSets.
- **The Engine:** How does it guarantee placement? Behind the scenes, the DaemonSet controller automatically injects strict **NodeAffinity** rules into the PodSpecs it generates. 
- **The Default Scheduler:** In older K8s architectures, the DaemonSet bypassed the `kube-scheduler` entirely. In modern Kubernetes, it relies entirely on the default scheduler evaluating that injected `NodeAffinity`.
- **Dynamic Scaling:** If a new Node joins the active cluster, a DaemonSet Pod is instantly scheduled onto it without any human intervention.

## 💻 Essential Execution (Commands & YAML)

**1. The DaemonSet YAML Definition**
*Note the critical difference from a ReplicaSet: You **CANNOT** specify a `replicas` count, because the count is mathematically directly tied to the number of nodes in your cluster.*
```yaml
apiVersion: apps/v1
kind: DaemonSet       # Switched from ReplicaSet
metadata:
  name: fluentd-agent
  namespace: kube-system
  labels:
    app: logging
spec:
  # NOTICE: There is NO 'replicas: X' field here!
  selector:
    matchLabels:
      name: fluentd-agent
  template:
    metadata:
      labels:
        name: fluentd-agent
    spec:
      containers:
      - name: fluentd
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
```

**2. Investigative CLI Commands**
```bash
# View all DaemonSets (Shorthand: ds)
kubectl get daemonset
kubectl get ds

# Deep dive into the configurations and status loops
kubectl describe ds fluentd-agent -n kube-system
```

## ⚠️ Production Gotchas & Interview Traps
- **The Production Gotcha (The Missing Pod):** Engineers deploy a DaemonSet and notice it created 3 Pods instead of 4 (one for each of their 4 Nodes). They usually forget about **Taints**. Standard DaemonSets *respect* taints. If Node #4 is heavily tainted and the DaemonSet lacks the corresponding Toleration, the Pod will refuse to schedule there.
- **The Principal SRE Interview Trap:** *"I deployed a Datadog monitoring DaemonSet to my entire cluster, but I am receiving zero metrics from my Control Plane (Master) nodes. Why, and how do I fix it?"*
  - **The SRE Answer:** "The Control Plane nodes are automatically protected by a `node-role.kubernetes.io/master:NoSchedule` Taint. Since your DaemonSet lacks a Toleration for this, it cannot place the agent on the Master nodes. To fix this, you must explicitly inject a `tolerations` block into the DaemonSet's `podSpec` targeting that exact Master node Taint."

## 🔍 Debugging (Where to look when it fails)
1. `kubectl get ds -A` : Look at the `DESIRED` vs `CURRENT` vs `READY` columns. If `DESIRED` is larger than `READY`, you have crashing instances.
2. `kubectl get pods -l <daemonset-label> -o wide` : Immediately maps out exactly which Pod wound up on which Node, helping you isolate visually which Node the DaemonSet failed to deploy on.

## 📝 10-Second Cheat Sheet
A **DaemonSet** ensures that exactly one replica of a Pod runs on every single eligible Node in the cluster via internal `NodeAffinity`, completely eliminating the need for `replicas` counts and serving as the backbone for cluster-wide networking (`kube-proxy`) and monitoring agents.
