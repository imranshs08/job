# 🚨 CKA Topic-Wise Mock Exam Tasks

> **Scope**: Interview & Exam Prep  
> **Note**: The CKA is 100% performance-based. You will not get multiple-choice questions. You will get access to a terminal and be asked to perform tasks exactly like the ones below.

---

## 1. 🗄️ Storage (PV & PVC) - *10% Weight*

**📝 Exam Scenario:**
> Create a Persistent Volume named `task-pv-volume` with storage capacity of `1Gi`, access mode `ReadWriteMany`, and hostPath `/etc/foo`. 
> Next, create a Persistent Volume Claim named `task-pv-claim` that requests `1Gi` and access mode `ReadWriteMany`. 
> Finally, create a pod named `task-pv-pod` using image `nginx` that mounts the volume at `/usr/share/nginx/html`.

**✅ Solution / Thought Process:**
*Note: Do not try to memorize the PV/PVC YAML. Go to the K8s Docs and search "Persistent Volumes" and copy the templates.*
1. Create `pv.yaml` from docs, apply it.
2. Create `pvc.yaml` from docs, apply it.
3. Stub the pod imperatively and add the mount:
```bash
kubectl run task-pv-pod --image=nginx --dry-run=client -o yaml > pod.yaml
vi pod.yaml # Add volumeMounts and volumes pointing to pvc
kubectl apply -f pod.yaml
```

---

## 2. 🚦 Services & Ingress - *20% Weight*

**📝 Exam Scenario:**
> A deployment named `api-deployment` exists traversing the `default` namespace. Expose it so that it is accessible *outside* the cluster on node port `30050`. Name the service `api-service`.

**✅ Solution (Imperative Speed is key!):**
```bash
kubectl expose deployment api-deployment --name=api-service --type=NodePort --port=8080 --target-port=80
```
*Wait, imperative expose chooses a random NodePort. We must edit it!*
```bash
kubectl edit svc api-service
# Change `nodePort: 31234` to `nodePort: 30050`
# Save and quit.
```

---

## 3. 🛡️ RBAC - *25% Weight*

**📝 Exam Scenario:**
> Create a ServiceAccount named `john` in the `backend` namespace. Create a ClusterRole named `secret-reader` that allows `get` and `watch` access to `Secrets`. Bind this ClusterRole to `john` restricting it strictly to the `backend` namespace. Name the binding `john-secret-access`.

**✅ Solution:**
```bash
kubectl create serviceaccount john -n backend
kubectl create clusterrole secret-reader --verb=get,watch --resource=secrets
# CRITICAL: A ClusterRole bound with a RoleBinding restricts its power to that specific namespace!
kubectl create rolebinding john-secret-access --clusterrole=secret-reader --serviceaccount=backend:john -n backend
```

---

## 4. 🚑 Advanced Troubleshooting - *30% Weight*

**📝 Exam Scenario:**
> A worker node named `node01` has stopped responding and its status is `NotReady`. Identify the issue, resolve it, and ensure the node comes back online.

**✅ Solution:**
1. `ssh node01`
2. `systemctl status kubelet`
3. Notice kubelet has failed.
4. `journalctl -u kubelet -f`
5. Usually on the exam, you will see a path error (e.g., config path `/var/lib/kubelet/config.yml` instead of `.yaml`), or Swap memory was left enabled.
6. Fix the file path in `/etc/systemd/system/kubelet.service.d/10-kubeadm.conf`.
7. `systemctl daemon-reload && systemctl restart kubelet`
8. `exit` back to master, run `kubectl get nodes`. It should be `Ready`.

---

## 5. 🏗️ Workloads & Scaling - *15% Weight*

**📝 Exam Scenario:**
> Scale the deployment `presentation-tier` in namespace `web` to 5 pods. Then, update the image of the pod to `nginx:1.19.8`. Record the rollout in the history.

**✅ Solution:**
```bash
kubectl scale deployment presentation-tier --replicas=5 -n web

# Use 'set image' and '--record' (if still supported by your k8s version context)
kubectl set image deployment/presentation-tier nginx=nginx:1.19.8 -n web

# Verify
kubectl rollout status deployment presentation-tier -n web
kubectl rollout history deployment presentation-tier -n web
```

---

## 6. 🧠 ETCD Backup (Guaranteed Question)

**📝 Exam Scenario:**
> Take a snapshot of the ETCD database and save it to `/opt/etcd-backup.db`. The ETCD database is running with mTLS authentication.

**✅ Solution:**
```bash
# Get the cert paths
cat /etc/kubernetes/manifests/etcd.yaml | grep file

# Run the snapshot
ETCDCTL_API=3 etcdctl snapshot save /opt/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

---

## 7. ☸️ Cluster Upgrades

**📝 Exam Scenario:**
> Upgrade the `kubeadm` master node to Kubernetes version `1.35.0` (or whatever the next version is). Make sure to safely evict all workloads before upgrading.

**✅ Solution:**
```bash
kubectl drain controlplane --ignore-daemonsets
apt-get update && apt-get install -y kubeadm=1.35.0-00
kubeadm upgrade plan
kubeadm upgrade apply v1.35.0
apt-get install -y kubelet=1.35.0-00 kubectl=1.35.0-00
systemctl daemon-reload && systemctl restart kubelet
kubectl uncordon controlplane
```
