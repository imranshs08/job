# CKA Cheat Sheet: Kubernetes Pods

> **Scope**: Core Concepts (Workloads)
> **Tracker Date**: Aug 25, 2026

The Pod is the smallest, most basic deployable object in Kubernetes. It represents a single instance of a running process in your cluster.

---

## 1. Core Pod Concepts

- **Shared Context:** Containers within a Pod share the same Network Namespace (IP address and port space) and can communicate via `localhost`.
- **Ephemeral Nature:** Pods are mortal. They are created, assigned a unique ID (UID), and scheduled to nodes where they remain until termination (or deletion). They do not self-heal on their own (which is why we use Deployments/ReplicaSets).
- **Multi-Container Pods:** Used for tightly coupled processes (e.g., a main web server container paired with a sidecar logging agent).

---

## 2. ⚡ Imperative Commands (CKA Speed Strategy)

Generating Pod YAML imperatively saves an enormous amount of time during the exam.

```bash
# Create and run a pod instantly
kubectl run my-nginx --image=nginx

# Generate Pod YAML without creating it (CRITICAL FOR CKA)
kubectl run my-nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Run a pod and attach an interactive shell
kubectl run tmp-shell --image=busybox -it --rm -- restart

# Add labels imperatively
kubectl run my-app --image=redis --labels="env=prod,tier=backend"

# Expose a pod instantly (creates a ClusterIP service)
kubectl expose pod my-nginx --port=80
```

---

## 3. Multi-Container Pods (Sidecar Pattern)

In the CKA, you may be asked to add a sidecar container to an existing pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: main-app
    image: busybox
    command: ['sh', '-c', 'echo Hello Kubernetes! && sleep 3600']
  - name: sidecar-logger
    image: busybox
    command: ['sh', '-c', 'tail -f /var/log/app.log']
```
*Note: To view logs of a specific container in a multi-container pod, specify the container name: `kubectl logs multi-container-pod -c sidecar-logger`*

---

## 4. Pod Lifecycle & Troubleshooting

- **Pending:** The Pod has been accepted by the Kubernetes cluster, but one or more container images have not been created. Check for scheduling issues (Taints, Node Selectors) via `kubectl describe pod`.
- **Running:** The Pod has been bound to a node, and all containers have been created.
- **CrashLoopBackOff:** The container is starting, crashing repeatedly, and K8s is backing off restarting it. Usually an application error or misconfigured `command`/`args`. Check with `kubectl logs <pod-name>`.
- **ImagePullBackOff:** K8s cannot pull the requested container image (typo in image name, authentication issue, or network block).

### 💡 CKA Debugging Flow
1. `kubectl get pods` (Observe the status)
2. `kubectl describe pod <pod-name>` (Look at the "Events" section at the bottom)
3. `kubectl logs <pod-name>` (Look at application-level errors)
```
