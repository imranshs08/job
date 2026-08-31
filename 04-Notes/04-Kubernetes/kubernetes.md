# 📝 Kubernetes — CKA Study Hub & Strategy

> **Phase:** 2 (September 2026) | **Target:** January 1, 2027

---

## 🎯 CKA Exam Breakdown & Strategy

- **Format:** Performance-based, Terminal-only. 15-20 Tasks. 2 Hours.
- **Passing Score:** 66%
- **Kubernetes Version:** ~v1.35 (As of late 2026)

### 📊 Official Weightage
1. **Troubleshooting (30%)** — *Highest Priority*
2. **Cluster Architecture, Install, Config (25%)**
3. **Services & Networking (20%)**
4. **Workloads & Scheduling (15%)**
5. **Storage (10%)**

### 🔥 The "Guaranteed" Exam Tasks (Most Important Areas)
You *must* be able to do these flawlessly from memory or by using `kubectl --help`:
- **ETCD Backup & Restore**: Taking a snapshot and restoring it to a new directory.
- **Cluster Upgrades**: Upgrading the primary node and a worker node from e.g. v1.34 to v1.35 using `kubeadm`.
- **Node Troubleshooting**: SSH'ing into a node, finding `kubelet` is dead because of a typo in `/var/lib/kubelet/config.yaml`, and fixing it.
- **Network Policies**: Creating a "default deny" policy and opening ingress specifically on port 80 for a specific pod.
- **Persistent Storage**: Creating a PVC and attaching it to a Pod.
- **RBAC**: Creating a specific ServiceAccount, Role, and RoleBinding to give an app restricted read-only permissions.

---

## 📚 Key Concepts & CKA Mock Tasks

| Concept | Notes | 🚨 Actual CKA / Similar Mock Task |
|---------|-------|------------------------------------|
| Pods | [✅ 01 Pods](01-CKA-Pods.md): Smallest deployable unit. Ephemeral. | *Create a multi-container pod running `nginx` & sidecar `busybox` writing to emptyDir.* |
| Deployments & ReplicaSets | [✅ 02 ReplicaSets](02-CKA-ReplicaSets.md) \| [✅ 03 Deployments](03-CKA-Deployments.md) | *Scale deployment to 5. Rolling update image to `nginx:1.19` & record it.* |
| Services | [✅ 04 Services](04-CKA-Services.md): Exposes pods to network via labels. | *Expose existing deployment via NodePort 30080 using imperative commands.* |
| Namespaces | [✅ 05 Namespaces](05-CKA-Namespaces.md): Isolation & resource quotas. | *Find all pods across namespaces consuming highest CPU and save to file.* |
| ConfigMaps & Secrets | [✅ 06 CM/Secrets](06-CKA-ConfigMaps-Secrets.md): Configuration decoupling. | *Create a secret from literal keys, mount as an environmental variable.* |
| PVs & PVCs | [✅ 07 Storage](07-CKA-Storage.md): StorageClasses & dynamic provisioning. | *Create 2Gi PVC (ReadWriteOnce). Create pod that mounts it to `/var/www/html`.* |
| StatefulSets & DaemonSets | [✅ 08 Workloads](08-CKA-StatefulSets-DaemonSets.md): Ordered deployment (DBs). | *Identify all untainted nodes and deploy a DaemonSet onto them.* |
| Probes, Resources, HPA | [✅ 09 Probes/HPA](09-CKA-Probes-Resources-HPA.md): Health checks/scaling. | *Add an HTTP Readiness probe to a pod so it only routes traffic when ready.* |
| RBAC | [✅ 10 RBAC](10-CKA-RBAC.md): Managing access scopes. | *Create ClusterRole allowing `get/list` on Secrets, bound to user `john`.* |
| Network Policies | [✅ 11 Network Policies](11-CKA-NetworkPolicies.md): K8s firewalls. | *Create NetworkPolicy blocking all traffic to `finance`, except from `team=audit`.* |
| Advanced Scheduling | [✅ 12 Scheduling](12-CKA-Scheduling.md): Taints, Tolerations, Affinity. | *Taint a node with `gpu=true:NoSchedule`. Create pod with matching toleration.* |
| CRDs & Operators | [✅ 13 CRDs](13-CKA-CRDs-Operators.md): Extending the K8s API. | *Identify all custom resource definitions currently active in the cluster.* |
| Cluster Upgrades | [✅ 14 Upgrades](14-CKA-Upgrades.md): Kubeadm upgrade nodes. | *Drain node01 gracefully. Upgrade kubeadm, kubelet, and kubectl.* |
| ETCD | [✅ 15 ETCD](15-CKA-ETCD-Backup.md): Snapshotting the cluster brain. | *Take an etcd snapshot using certificates in `/etc/kubernetes/pki/etcd/`.* |
| Troubleshooting | [✅ 16 Troubleshooting](16-CKA-Troubleshooting.md): Kubelet, CNI. | *A worker node is `NotReady`. Find why `kubelet` is crash-looping and restore it.* |
| CoreDNS & Networking | [✅ 17 CoreDNS](17-CKA-CoreDNS.md): DNS resolution & FQDNs. | *Run an nslookup on a service from a busybox pod and resolve its cluster IP.* |
| Ingress Controllers | [✅ 18 Ingress](18-EKS-NGINX-Ingress.md): External L7 routing. | *Create Ingress resource routing `/app1` to service A and `/app2` to service B.* |

---

## ⚡ CKA Imperative Commands Cheat Sheet

*Write YAML fast during the exam to save precious minutes!*

```bash
# Generate Pod YAML without creating
kubectl run my-nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Create Deployment instantly
kubectl create deployment app --image=img --replicas=3

# Expose a Deployment via NodePort instantly
kubectl expose deployment frontend --name=frontend-svc --type=NodePort --port=80 --target-port=8080

# Change Context (Fastly switch namespaces)
kubectl config set-context --current --namespace=web-prod

# Find dead pods
kubectl get pods --field-selector=status.phase=Failed -A

# Test RBAC Permissions
kubectl auth can-i delete pods --as=system:serviceaccount:dev:john -n dev
```

---

## 🎤 Interview Q&A Bank

| # | Question | Core Answer Frame (STAR Method prep) |
|---|----------|----------------------------------------|
| 1 | Explain Kubernetes architecture | *Control plane (API, etcd, scheduler, CM) vs Worker (Kubelet, Kube-proxy, Container Runtime).* |
| 2 | Deployment vs StatefulSet? | *Deployments are stateless (random hash). StatefulSets have sticky identity (db-0, db-1) and ordered spin-ups.* |
| 3 | How does a Service discover Pods? | *Through matching the `selector` against pod labels, which automatically populates an `Endpoints` object.* |
| 4 | Explain RBAC in Kubernetes | *Role (what you can do) + RoleBinding (who you are tying it to).* |
| 5 | How do you troubleshoot a CrashLoopBackOff? | *1. `kubectl describe pod` for events. 2. `kubectl logs <pod>` for app errors. 3. Check OOMKill or Liveness probe failures.* |
