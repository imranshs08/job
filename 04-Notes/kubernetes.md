# 📝 Kubernetes — Study Notes

> **Phase:** 2 (September 2026) | **Playlist:** Day 21–28

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| K8s Architecture (control plane, workers) | |
| Pods (single, multi-container, init) | |
| Deployments & ReplicaSets | |
| Services (ClusterIP, NodePort, LoadBalancer) | |
| Ingress & Ingress Controllers | |
| Namespaces | |
| ConfigMaps & Secrets | |
| Persistent Volumes & PVCs | |
| StatefulSets | |
| DaemonSets | |
| RBAC (Roles, ClusterRoles, Bindings) | |
| Probes (Liveness, Readiness, Startup) | |
| Resource Limits & Requests | |
| Horizontal Pod Autoscaler | |
| Network Policies | |
| Custom Resource Definitions (CRDs) | |
| Operators | |

---

## Commands Cheat Sheet

```bash
# Cluster Info
kubectl cluster-info
kubectl get nodes
kubectl get all -A

# Pods
kubectl run nginx --image=nginx
kubectl get pods -o wide
kubectl describe pod <name>
kubectl logs <pod> -f
kubectl exec -it <pod> -- bash
kubectl delete pod <name>

# Deployments
kubectl create deployment app --image=img --replicas=3
kubectl scale deployment app --replicas=5
kubectl rollout status deployment app
kubectl rollout undo deployment app

# Services
kubectl expose deployment app --port=80 --type=NodePort
kubectl get svc

# Config
kubectl create configmap cm --from-literal=key=val
kubectl create secret generic sec --from-literal=pw=123

# Troubleshooting
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods
kubectl top nodes
```

---

## Hands-On Lab Notes

### Lab 1: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

### Lab 2: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

---

## Interview Q&A

| # | Question | My Answer |
|---|----------|-----------|
| 1 | Explain Kubernetes architecture | |
| 2 | What is the difference between Deployment and StatefulSet? | |
| 3 | How does a Service discover Pods? | |
| 4 | What are Probes and why are they important? | |
| 5 | Explain RBAC in Kubernetes | |
| 6 | How does Horizontal Pod Autoscaler work? | |
| 7 | What is an Ingress Controller? | |
| 8 | How do you handle secrets in K8s? | |
| 9 | What is a CRD and Operator? | |
| 10 | How do you troubleshoot a pod stuck in CrashLoopBackOff? | |

---

## Resources
- [ ] Playlist: Day 21–28
- [ ] Kubernetes Documentation (kubernetes.io)
- [ ] KillerCoda (interactive labs)
