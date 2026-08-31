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

---

## 8. 🛡️ Network Policies

**📝 Exam Scenario:**
> In the `finance` namespace, create a NetworkPolicy named `deny-all-ingress` that denies all incoming traffic to all pods in the namespace.

**✅ Solution:**
```yaml
# You must write this from memory or K8s docs
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: finance
spec:
  podSelector: {} # Empty selector selects all pods
  policyTypes:
  - Ingress
  # Leaving the 'ingress' block empty denies everything by default
```

---

## 9. 🧠 Scheduling (Taints & Tolerations)

**📝 Exam Scenario:**
> Taint node `node02` with `key=disktype`, `value=nvme`, and effect `NoSchedule`. Then create a pod named `fast-db` with image `redis` that can tolerate this taint and schedule onto `node02`.

**✅ Solution:**
```bash
# 1. Taint the node
kubectl taint nodes node02 disktype=nvme:NoSchedule

# 2. Stub the pod
kubectl run fast-db --image=redis --dry-run=client -o yaml > pod.yaml

# 3. Add the toleration to pod.yaml under spec:
#  tolerations:
#  - key: "disktype"
#    operator: "Equal"
#    value: "nvme"
#    effect: "NoSchedule"

kubectl apply -f pod.yaml
```

---

## 10. 🔐 Secrets & Env Variables

**📝 Exam Scenario:**
> Create a secret named `db-creds` with the key `password` and value `secure123!`. Then, create a pod named `webapp` using image `nginx` that loads this secret into an environment variable named `DB_PASS`.

**✅ Solution:**
```bash
# 1. Create the secret imperatively
kubectl create secret generic db-creds --from-literal=password=secure123!

# 2. Stub the pod
kubectl run webapp --image=nginx --dry-run=client -o yaml > pod.yaml

# 3. Modify pod.yaml -> under containers[0], add:
#    env:
#    - name: DB_PASS
#      valueFrom:
#        secretKeyRef:
#          name: db-creds
#          key: password

kubectl apply -f pod.yaml
```

---

## 11. 🔍 Log Analysis & Grep

**📝 Exam Scenario:**
> Find the pod in the `production` namespace that is generating the error `OutOfMemory`. Extract that specific log line and write it to `/opt/oom-error.txt`.

**✅ Solution:**
```bash
# Loop through pods or guess the failing one based on `kubectl get pods -n production` restarts.
kubectl logs <failing-pod-name> -n production | grep "OutOfMemory" > /opt/oom-error.txt
```

---

## 12. 📊 Sorting & Fields (Very Common!)

**📝 Exam Scenario:**
> Find the node in the cluster that has the highest memory utilization and write its name to `/opt/highest-mem-node.txt`.

**✅ Solution:**
```bash
# Use kubernetes metrics-server output
kubectl top nodes --sort-by=memory
# Look at the top node, then write its name to the file:
echo "node01" > /opt/highest-mem-node.txt
```

---

## 13. 📦 Multi-Container Pods (EmptyDir)

**📝 Exam Scenario:**
> Create a pod named `shared-log-app`. 
> Container 1: named `app`, image `busybox`, running `while true; do echo 'app running' >> /var/log/app.log; sleep 5; done`.
> Container 2: named `sidecar`, image `busybox`, running `tail -f /var/log/app.log`.
> They must share an `emptyDir` volume mounted at `/var/log`.

**✅ Solution:**
1. Generate pod stub: `kubectl run shared-log-app --image=busybox --dry-run=client -o yaml > pod.yaml`
2. Hand-edit the manifest to add the second container, the commands, and the volume mounts:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shared-log-app
spec:
  containers:
  - name: app
    image: busybox
    command: ["/bin/sh", "-c", "while true; do echo 'app running' >> /var/log/app.log; sleep 5; done"]
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
  - name: sidecar
    image: busybox
    command: ["/bin/sh", "-c", "tail -f /var/log/app.log"]
    volumeMounts:
    - name: log-volume
      mountPath: /var/log
  volumes:
  - name: log-volume
    emptyDir: {}
```

---

## 14. ⏱️ Init Containers

**📝 Exam Scenario:**
> Create a pod named `db-init-test` running image `mysql`. The pod should not start until an InitContainer named `wait-for-service` running `busybox` successfully pings `10.0.0.1`.

**✅ Solution:**
1. Stub it out.
2. Add the `initContainers` block directly above the `containers` block:
```yaml
  initContainers:
  - name: wait-for-service
    image: busybox
    command: ['sh', '-c', 'until ping -c 1 10.0.0.1; do echo waiting; sleep 2; done;']
```

---

## 15. 📍 Node Affinity

**📝 Exam Scenario:**
> Create a deployment named `gpu-workload` with 2 replicas using image `nginx`. Ensure these pods are scheduled *only* on nodes carrying the label `hardware=gpu`. (Assume the nodes are already labeled).

**✅ Solution:**
1. `kubectl create deployment gpu-workload --image=nginx --replicas=2 --dry-run=client -o yaml > dep.yaml`
2. Add the `nodeSelector` (the simplest form of affinity) under the pod spec template (NOT the deployment spec!):
```yaml
    spec:
      nodeSelector:
        hardware: gpu
      containers:
      - image: nginx
```
*(If the question explicitly asks for `nodeAffinity`, you must use the longer `affinity:` block).*
