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
| Pods | [✅ Cheat Sheet](CKA-Pods-CheatSheet.md): Smallest deployable unit. Ephemeral, shares network/storage namespace. | *Create a multi-container pod running `nginx` and a sidecar `busybox` container writing to a shared emptyDir.* |
| Deployments & ReplicaSets | [✅ Deployments](CKA-Deployments-CheatSheet.md) \| [✅ ReplicaSets](CKA-ReplicaSets-CheatSheet.md): Stateless apps, rollouts, self-healing. | *Scale a deployment to 5 replicas. Then perform a rolling update of the image to `nginx:1.19` and record it.* |
| Services | [✅ Cheat Sheet](CKA-Services-CheatSheet.md): Exposes pods to network via labels. ClusterIP (internal), NodePort (static port). | *Expose an existing deployment via a NodePort service on port 30080 using imperative commands.* |
| Ingress Controllers | [✅ Guide](EKS-NGINX-Ingress.md): External L7 routing (e.g. NGINX, AGC). | *Create an Ingress resource routing `/app1` to service A and `/app2` to service B.* |
| Namespaces | [✅ Cheat Sheet](CKA-Namespaces-CheatSheet.md): Virtual clusters for isolation & resource quotas. | *Find all pods across all namespaces consuming the highest CPU and write their names to a file.* |
| ConfigMaps & Secrets | [✅ Cheat Sheet](CKA-ConfigMaps-Secrets-CheatSheet.md): Configuration decoupling and base64 encoded secrets. | *Create a secret from literal keys, mount it as an environmental variable in a specific pod.* |
| PVs & PVCs | [✅ Storage](CKA-Storage-PV-PVC-CheatSheet.md): StorageClasses, dynamic provisioning, and PV binding. | *Create a 2Gi PVC requesting ReadWriteOnce. Create a pod that mounts it to `/var/www/html`.* |
| StatefulSets & DaemonSets | [✅ Workloads](CKA-StatefulSets-DaemonSets-CheatSheet.md): Ordered deployment (DBs) and per-node agents. | *Identify all nodes without a specific taint and deploy a DaemonSet onto them.* |
| RBAC | [✅ Cheat Sheet](CKA-RBAC-CheatSheet.md): Managing access scopes. RoleBinding vs ClusterRoleBinding. | *Create a ClusterRole allowing `get/list` on Secrets, and bound it to the user `john`.* |
| Network Policies | [✅ Cheat Sheet](CKA-NetworkPolicies-CheatSheet.md): K8s firewalls. Ingress/Egress Default Deny strategies. | *Create a NetworkPolicy blocking all traffic to namespace `finance`, except from pods labeled `team=audit`.* |
| Advanced Scheduling | [✅ Cheat Sheet](CKA-Scheduling-Taints-Affinity.md): Taints, Tolerations, Node Affinity. | *Taint a node with `gpu=true:NoSchedule`. Create a pod with a matching toleration to land on it.* |
| Cluster Upgrades | [✅ Cheat Sheet](CKA-Kubeadm-Upgrades-CheatSheet.md): Kubeadm upgrade master vs worker nodes. | *Drain node01 gracefully. Upgrade kubeadm, kubelet, and kubectl to the next minor version.* |
| ETCD | [✅ Cheat Sheet](CKA-ETCD-Backup-Reset-CheatSheet.md): Snapshotting the cluster brain. | *Take an etcd snapshot using the certificates located in `/etc/kubernetes/pki/etcd/`.* |
| Troubleshooting | [✅ Cheat Sheet](CKA-Advanced-Troubleshooting.md): Kubelet crashes, CNI failures, static pods. | *A worker node is `NotReady`. Find out why `kubelet` is crash-looping and restore the node.* |

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
