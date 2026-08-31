# CKA Cheat Sheet: Probes, Resources, & HPA

> **Scope**: Scheduling & Autoscaling  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

Healthy clusters rely on intelligent scheduling and self-healing. Probes ensure traffic only hits healthy pods, Resources ensure predictable scheduling, and the HPA scales them according to demand.

---

## 1. Container Probes (Health Checks)

- **LivenessProbe**: Answers "Is the container running correctly?" If it fails, K8s **restarts** the container. (Prevents deadlocked apps).
- **ReadinessProbe**: Answers "Is the container ready to receive HTTP traffic?" If it fails, K8s **removes the Pod from the Service's Endpoints**. (Prevents traffic from hitting a pod that is still booting up or overloaded).
- **StartupProbe**: Runs *before* the others. For legacy apps that take 2 minutes to boot. Once it passes, Liveness/Readiness take over.

### YAML snippet to memorize:
```yaml
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
```

---

## 2. Resource Requests vs. Limits

In K8s, `1 CPU = 1 vCPU = 1000m (millicores)`.

- **Requests**: What the pod is **guaranteed** to get. The Scheduler uses this to find a Node with enough free space. If no node has this amount of free CPU/RAM, the pod stays `Pending`.
- **Limits**: The absolute **maximum** a pod can use. 
  - If a pod exceeds its CPU Limit, it is **throttled** (slows down).
  - If a pod exceeds its Memory Limit, it is **OOMKilled** (Out Of Memory Killed) and restarted.

```yaml
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### 💡 CKA Troubleshooting Tip
If a pod is stuck in `Pending`, check `kubectl describe pod`. Often it's because `Insufficient cpu` or `Insufficient memory` on all nodes based on your `requests`.

---

## 3. Horizontal Pod Autoscaler (HPA)

The HPA automatically scales the number of Pods in a Deployment/ReplicaSet based on observed CPU/Memory utilization. 
*Note: HPA requires the `metrics-server` to be installed on the cluster.*

### ⚡ Imperative Command (Fastest way on Exam):
```bash
# Autoscale a deployment between 2 and 10 pods, triggering when CPU hits 80% usage
kubectl autoscale deployment my-app --cpu-percent=80 --min=2 --max=10
```

### Verification:
```bash
kubectl get hpa
# Look at the 'TARGETS' column. If it says <unknown>/80%, the metrics-server is missing or the pods don't have 'resources.requests' defined!
```

> **Critical Dependency**: The HPA **cannot** scale a Deployment if the Pods do not have CPU `requests` defined in their YAML! K8s cannot calculate a percentage if there is no baseline request.
