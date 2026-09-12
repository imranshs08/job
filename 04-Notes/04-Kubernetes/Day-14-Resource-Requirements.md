# 📘 Kubernetes Resource Requirements & Live Editing

## 🎯 The "Why" (Core Concept)
- **Concept:** Every Pod requires raw CPU and Memory to function. Kubernetes allows you to define exactly what a Pod expects to consume (**Requests**) and the absolute maximum boundary it is legally allowed to consume (**Limits**).
- **The Analogy:** Think of a Hotel Reservation. The **Request** is you calling ahead to ensure a room is strictly blocked out for you (the Scheduler guaranteeing a Node actually has enough free space perfectly reserved for your pod). The **Limit** is the hotel aggressively cutting off your room service tab at $500 so you don't bankrupt them (the Kubelet killing your pod if it consumes too much node RAM). 
- **Catastrophic Problem Solved:** It prevents the **"Noisy Neighbor"** catastrophe. Without Limits, a single memory-leaking pod could rapidly consume 100% of a Node's RAM, violently crashing every other production microservice running on that exact same hardware.

## ⚙️ Architecture & Under the Hood
- **Requests vs. Limits:** The `kube-scheduler` only cares about *Requests* (to find a suitable node). The `kubelet` (the agent on the node itself) only cares about *Limits* (executing the Kill command).
- **Compressible vs Non-Compressible Assets:** 
  - **CPU is Compressible:** If a pod tries to exceed its CPU limit, Kubernetes will simply throttle (slow down) the CPU allocation. The pod will lag, but it will *not* be killed.
  - **Memory is Non-Compressible:** If a pod attempts to allocate even 1 byte over its Memory limit, the Linux kernel immediately throws an `OOMKilled` (Out Of Memory) exception and violently terminates the process.
- **Namespaces:** To stop developers from forgetting to add limits, cluster admins configure **LimitRanges** (default limits injected automatically) and **ResourceQuotas** (maximum capacity bounds for an entire Namespace).

## 💻 Essential Execution (Commands & YAML)

**1. The Resources YAML Block**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend-database
spec:
  containers:
  - name: postgres
    image: postgres
    resources:
      requests:
        memory: "256Mi"  # The scheduler guarantees this is available
        cpu: "500m"      # 500 millicores (half of a CPU core)
      limits:
        memory: "512Mi"  # If it hits 513Mi, the kernel executes OOMKilled
        cpu: "1"         # 1 Full CPU core (will throttle if it wants more)
```

**2. LimitRange (Default Automations)**
Limits only work if developers actually write them. A `LimitRange` automatically injects default Requests/Limits into Pods that forget them, ensuring the cluster stays safe.
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
spec:
  limits:
  - default:           # The Limit applied if the pod forgets to specify one
      cpu: 500m
      memory: 512Mi
    defaultRequest:    # The Request applied if the pod forgets to specify one
      cpu: 500m
      memory: 256Mi
    type: Container
```

**3. ResourceQuota (Hard Namespace Limits)**
A `ResourceQuota` places an absolute ceiling on an entire *Namespace*. If the combined resource requests of all Pods in the namespace exceed this quota, the deployment is blocked.
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "1"         # Max 1 Total CPU across all Pods in this Namespace
    requests.memory: 1Gi      # Max 1GB Total RAM across all Pods in this Namespace
    limits.cpu: "2"
    limits.memory: 2Gi
```

**4. The Live Editing Limitation**
```bash
# 1. Attempting to live-edit a running Pod
kubectl edit pod webapp

# IMPORTANT: Kubernetes physically FORBIDS editing most specs (like env vars or limits) of a live Pod. 
# It will reject your save and dump your edits into a temporary /tmp/ file.
# You must manually delete the original, and recreate it from the temp file:
kubectl delete pod webapp
kubectl create -f /tmp/kubectl-edit-ccvrq.yaml

# 2. Live-editing a Deployment (The Correct Way)
kubectl edit deployment my-deployment
# Deployments natively allow infinite edits because they automatically 
# spin up an entirely new Pod and seamlessly terminate the old one.
```

## ⚠️ Production Gotchas & Interview Traps
- **The Production Gotcha (The Uneditable Pod):** Junior engineers routinely panic when `kubectl edit pod` is rejected by the API server. You can practically *only* edit `spec.containers[*].image`, `tolerations`, and `activeDeadlineSeconds` on a live bare pod. For any other structural change, you mathematically must destroy and recreate it.
- **The Principal SRE Interview Trap:** *"A developer complains their Python pod was OOMKilled, but their identically configured Java pod just got extremely slow without crashing. Why did this happen?"*
  - **The SRE Answer:** "This is the fundamental difference between resource types. The Java pod likely hit its **CPU Limit**, which is a compressible resource, resulting in heavy CPU throttling. The Python pod hit its **Memory Limit**. Memory is strictly non-compressible at the Linux cgroup level; the instant it is breached, the kernel OOM-killer intervenes to protect the Node."

## 🔍 Debugging (Where to look when it fails)
1. `kubectl describe pod <pod-name>` : Scroll to `State:` to explicitly see `Terminated: OOMKilled` alongside the exact exit code `137`.
2. `kubectl get events --sort-by='.metadata.creationTimestamp'` : Broadly monitors the namespace for Kubelet throttling or OOMkill warnings dynamically in real-time.

## 📝 10-Second Cheat Sheet
**Requests** guarantee that the `kube-scheduler` finds a large enough Node, while **Limits** instruct the `kubelet` to aggressively throttle CPU or violently `OOMKill` Memory spikes to protect the broader cluster infrastructure.
