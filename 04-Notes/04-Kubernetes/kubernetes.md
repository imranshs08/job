# 📝 Kubernetes — Study Notes

> **Phase:** 2 (September 2026) | **Playlist:** Day 21–28

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| K8s Architecture (control plane, workers) | |
| Pods (single, multi-container, init) | [✅ See Cheat Sheet](CKA-Pods-CheatSheet.md): Smallest deployable unit. Ephemeral, shares network/storage namespace. |
| Deployments & ReplicaSets | [✅ See Deployments](CKA-Deployments-CheatSheet.md) \| [✅ See ReplicaSets](CKA-ReplicaSets-CheatSheet.md): Manages stateless apps, declarative rollouts, self-healing. |
| Services (ClusterIP, NodePort, LoadBalancer) | [✅ See Cheat Sheet](CKA-Services-CheatSheet.md): Exposes pods to network via labels. ClusterIP (internal), NodePort (static port). |
| Ingress & Ingress Controllers | [✅ See Guide](AGIC-to-AGC-Migration.md): External L7 routing (e.g. NGINX, AGC). |
| Namespaces | [✅ See Cheat Sheet](CKA-Namespaces-CheatSheet.md): Virtual clusters for isolation & resource quotas. |
| ConfigMaps & Secrets | [✅ See Cheat Sheet](CKA-ConfigMaps-Secrets-CheatSheet.md): Configuration decoupling and base64 encoded secrets. |
| Persistent Volumes & PVCs | [✅ See Storage](CKA-Storage-PV-PVC-CheatSheet.md): StorageClasses, dynamic provisioning, and PV binding. |
| StatefulSets | [✅ See Workloads](CKA-StatefulSets-DaemonSets-CheatSheet.md): Ordered deployment, sticky identity, headless services. |
| DaemonSets | [✅ See Workloads](CKA-StatefulSets-DaemonSets-CheatSheet.md): Running a pod clone on every node (logs/monitoring). |
| RBAC (Roles, ClusterRoles, Bindings) | [✅ See Cheat Sheet](CKA-RBAC-CheatSheet.md): Managing access scopes. RoleBinding vs ClusterRoleBinding. |
| Probes (Liveness, Readiness, Startup) | [✅ See Probes & Scaling](CKA-Probes-Resources-HPA-CheatSheet.md): Health checks that trigger restarts or block routing. |
| Resource Limits & Requests | [✅ See Probes & Scaling](CKA-Probes-Resources-HPA-CheatSheet.md): CPU/Mem baseline requests and throttling limits. |
| Horizontal Pod Autoscaler | [✅ See Probes & Scaling](CKA-Probes-Resources-HPA-CheatSheet.md): Native load-based scaling requiring metrics-server. |
| Network Policies | [✅ See Cheat Sheet](CKA-NetworkPolicies-CheatSheet.md): K8s firewalls. Ingress/Egress Default Deny strategies. |
| Custom Resource Definitions (CRDs) | [✅ See CRDs & Operators](CKA-CRD-Operators-CheatSheet.md): Extending the K8s API with custom schemas. |
| Operators | [✅ See CRDs & Operators](CKA-CRD-Operators-CheatSheet.md): Custom controllers executing the CRD logic in real-time. |

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
