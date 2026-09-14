# 📘 Priority Classes

## 🎯 The "Why" (Core Concept)
**Kubernetes Priority Classes** are the cluster's **importance ranking system** that dictates which workloads get scheduled first, and more importantly, which workloads get assassinated (evicted) when the cluster runs out of CPU or memory. 

*Analogy:* Imagine a crowded VIP nightclub (the Kubernetes Node) with a strict bouncer (the `kube-scheduler`). If a high-paying celebrity (Critical DB Pod) arrives and the club is at capacity, the bouncer will literally kick out regular patrons (Batch Jobs/Low-priority Pods) onto the street to make room for the VIP. 

**What catastrophic problem does this solve?**
Without Priority Classes, Kubernetes schedules pods democratically on a first-come, first-served basis. If a cluster experiences resource exhaustion, a critical payment API might be left in a `Pending` state while a low-priority background logging job consumes all available CPU. Priority Classes ensure **guaranteed scheduling for mission-critical applications through preemption**.

## ⚙️ Architecture & Under the Hood
*   **The Value Range:** Priority values are integers ranging from `-1,000,000,000` to `1,000,000,000` (One Billion). Higher values mean higher priority.
*   **System Critical Range:** Kube-system components (like `coredns` or `kube-proxy`) use reserved priority values strictly above 1 billion (`2,000,000,000` for `system-cluster-critical` and `2,000,001,000` for `system-node-critical`) so they are never evicted by user workloads.
*   **The Preemption Mechanic:** When a high-priority pod arrives and finds no nodes with sufficient resources, the `kube-scheduler` simulates removing lower-priority pods. If removing them frees enough space, it triggers **Preemption**, gracefully terminating (SIGTERM) the lower-priority pods.
*   **Global Default Fallback:** If a pod is deployed without specifying a `priorityClassName`, its priority fundamentally defaults to `0`. However, you can configure exactly one PriorityClass across the entire cluster with `globalDefault: true` to shift this baseline.
*   **Categorical Stratification:** In a production architecture, SREs strictly categorize workloads:
    *   *System Components (Control Plane elements):* > 2 Billion (Reserved)
    *   *Databases / StatefulSets:* ~800 Million
    *   *Critical Apps / Customer APIs:* ~500 Million
    *   *Stateless Microservices:* ~100 Million
    *   *Batch Jobs / CronJobs:* ~10,000
*   **Non-Preempting Priority:** Kubernetes v1.24+ supports `PreemptionPolicy: Never`. High-priority pods will wait at the front of the scheduling queue but will *not* violently evict running pods to fit in. 

## 💻 Essential Execution (Commands & YAML)

### 1. View Existing Priority Classes
```bash
# List all priority classes in the cluster (including the built-in system ones)
kubectl get priorityclass

# View the exact integer value and global status of a specific class
kubectl get priorityclass system-cluster-critical -o yaml
```

### 2. Creating a Custom Priority Class (YAML)
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-database-priority
value: 800000000           # The raw integer weight (Max 1 Billion for users)
globalDefault: false       # Set to 'true' ONLY if you want all generic pods to inherit this
description: "Used exclusively for stateful database pods that must never be evicted."
preemptionPolicy: PreemptLowerPriority  # Alternatively set to 'Never' to queue without killing
```

### 3. Creating a Global Default Priority Class (YAML)
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: baseline-default-priority
value: 1000                # Every pod without a defined class will now start at 1000
globalDefault: true        # SUPER IMPORTANT: Only one class can have this set to true!
description: "The default priority for standard web workloads."
```

### 4. Assigning a Priority Class to a Pod or Deployment (YAML)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: production-postgresql
  labels:
    app: database
spec:
  containers:
  - name: postgres
    image: postgres:15
  priorityClassName: critical-database-priority # MUST exactly match the PriorityClass metadata.name
```

## ⚠️ Production Gotchas & Interview Traps
*   **The Gotcha (The Cascading Failure Trap):** A junior engineer assigns max priority (1 Billion) to a frontend deployment with an aggressive HPA (Horizontal Pod Autoscaler). During a traffic spike, the HPA scales the frontend aggressively, and because it has max priority, the cluster begins preempting and evicting all backend APIs and middle-tier microservices to make room. The frontend survives, but the app breaks because the database/backend was murdered.
*   **The Interview Trap:** "What happens if two pods have the exact same priority class but there's only room for one?"
    *   *The SRE Answer:* The `kube-scheduler` falls back to secondary scheduling factors: QoS (Quality of Service) classes (`Guaranteed` > `Burstable` > `BestEffort`), Pod disruption budgets, and resource request alignments.
*   **The Unintended Default:** Activating `globalDefault: true` in an existing cluster automatically applies that priority logic to all *future* pods without a class, but does NOT retroactively change the integer value of currently running pods until they are recreated.

## 🔍 Debugging (Where to look when it fails)
If pods are inexplicably stuck in `Pending` or being unexpectedly evicted:

1.  **Check the Events logs for preemption triggers:**
    ```bash
    kubectl get events --sort-by='.metadata.creationTimestamp' | grep -i preempt
    ```
2.  **Describe the Pending Pod to see why it won't evict others:**
    ```bash
    kubectl describe pod <pending-pod-name>
    # Look for: "0/5 nodes are available: 5 Insufficient cpu. preemption: 0/5 nodes are available: 5 No preemption victims found for incoming pod."
    ```
3.  **Audit the active Priority Classes:**
    ```bash
    kubectl get priorityclasses
    # Ensure no developer created a rogue "1 Billion" class that is hoarding resources
    ```
4.  **Check Kube-Scheduler Logs:**
    ```bash
    kubectl logs -n kube-system -l component=kube-scheduler
    # Useful for debugging why preemption logic bypassed certain workloads
    ```
5.  **Verify Pod Priorities on a specific Node:**
    ```bash
    kubectl get pods --all-namespaces --field-selector spec.nodeName=<node-name> -o custom-columns=NAME:.metadata.name,PRIORITY:.spec.priority
    ```

## 📝 10-Second Cheat Sheet
Priority Classes prevent critical workloads from hanging in a `Pending` state by actively preempting (killing) lower-priority pods to free up resources. Priority values range from 1 to 1 Billion for users, while core Kubernetes components use reserved values > 2 Billion. You attach them to Pods using `priorityClassName: <name>`. Beware: giving overly high priority to autoscaling deployments is an easy way to accidentally nuke your entire backend infrastructure during a spike.
