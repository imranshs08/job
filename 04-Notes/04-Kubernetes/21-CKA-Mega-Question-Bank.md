# 🏆 CKA Mega Question Bank (Real Exam Format)

> **Scope:** Intense repetition for CKA Muscle Memory.  
> **Note:** The actual CKA exam contains 15-20 questions. These scenarios are formatted to mimic the **exact UI and layout** you will see on the exam screen (Context, Weight, Task). 

---

## 🛠️ Domain 1: Workloads & Scheduling (15%)

**Q1. Core Workloads**
> **Context:** `kubectl config use-context k8s-web-1`
> **Weight:** 4%
> 
> **Task:**
> Create a new `Pod` named `nginx-pod` in the `web` namespace.
> - Use the image `nginx:alpine`.
> - The container must request `200m` CPU.
> - Expose the container on port `80`.

**✅ Solution:** 
`kubectl run nginx-pod --image=nginx:alpine -n web --requests=cpu=200m --port=80`

---

**Q2. Scaling & Updates**
> **Context:** `kubectl config use-context k8s-db-1`
> **Weight:** 5%
> 
> **Task:**
> A deployment named `redis-deploy` exists in the `default` namespace.
> - Scale this deployment up to `5` replicas.
> - Perform a rolling update changing the image to `redis:7`.
> - Ensure the rollout is recorded in the annotation history.

**✅ Solution:**
```bash
kubectl scale deployment redis-deploy --replicas=5
kubectl set image deployment/redis-deploy redis=redis:7 --record
# Verify it: kubectl rollout status deployment redis-deploy
```

---

**Q3. Taints & Tolerations**
> **Context:** `kubectl config use-context k8s-sched-1`
> **Weight:** 6%
> 
> **Task:**
> - Apply a taint to the node `worker-2` with the key `env`, value `prod`, and effect `NoSchedule`.
> - Create a new Pod named `toleration-pod` using image `busybox` that can tolerate this taint and will run on `worker-2`. It should run the command `sleep 3600`.

**✅ Solution:**
```bash
kubectl taint node worker-2 env=prod:NoSchedule
kubectl run toleration-pod --image=busybox --dry-run=client -o yaml --command -- sleep 3600 > pod.yaml
vi pod.yaml # Add tolerations block under spec:
#  tolerations:
#  - key: "env"
#    operator: "Equal"
#    value: "prod"
#    effect: "NoSchedule"
kubectl apply -f pod.yaml
```

---

**Q4. Node Selector Affinity**
> **Context:** `kubectl config use-context k8s-sched-2`
> **Weight:** 4%
> 
> **Task:**
> - Assign the label `diskType=ssd` to the node `worker-1`.
> - Deploy a pod named `ssd-pod` using image `nginx` that specifically requests to be scheduled on nodes with the `diskType=ssd` label.

**✅ Solution:**
```bash
kubectl label node worker-1 diskType=ssd
kubectl run ssd-pod --image=nginx --dry-run=client -o yaml > pod.yaml
vi pod.yaml # Add nodeSelector block under spec:
#  nodeSelector:
#    diskType: ssd
kubectl apply -f pod.yaml
```

---

**Q5. Manual Scheduling (No Scheduler)**
> **Context:** `kubectl config use-context k8s-sched-3`
> **Weight:** 7%
> 
> **Task:**
> The `kube-scheduler` is disabled globally.
> - Forcefully deploy a pod named `manual-pod` utilizing image `nginx` onto the node `master-node` bypassing the scheduler entirely.

**✅ Solution:**
```bash
kubectl run manual-pod --image=nginx --dry-run=client -o yaml > pod.yaml
vi pod.yaml # Add nodeName block under spec:
#  nodeName: master-node
kubectl apply -f pod.yaml
```

---

## 🚦 Domain 2: Services & Networking (20%)

**Q6. Exposing Internal Services**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 4%
> 
> **Task:**
> A deployment named `frontend` exists. 
> - Expose it internally so other pods in the cluster can communicate with it on port `80`. 
> - Name the new service `front-svc`.

**✅ Solution:**
`kubectl expose deployment frontend --name=front-svc --port=80 --type=ClusterIP`

---

**Q7. NodePort External Exposure**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 6%
> 
> **Task:**
> A pod named `db` is listening on port `5432`.
> - Expose it externally so that traffic hitting any worker node on port `32000` routes to this pod.
> - Name the service `db-svc`.

**✅ Solution:**
```bash
kubectl expose pod db --name=db-svc --port=5432 --type=NodePort
kubectl edit svc db-svc # Manually change the nodePort field to 32000 and save.
```

---

**Q8. Network Policies (Restrictive)**
> **Context:** `kubectl config use-context k8s-net-2`
> **Weight:** 8%
> 
> **Task:**
> In the namespace `restricted`, deny all outgoing (egress) traffic from all pods by default.
> - Create a NetworkPolicy named `deny-egress` to achieve this.

**✅ Solution:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress
  namespace: restricted
spec:
  podSelector: {}
  policyTypes:
  - Egress
  # Leaving the egress block completely absent denies all.
```

---

**Q9. DNS Resolution Testing**
> **Context:** `kubectl config use-context k8s-net-3`
> **Weight:** 5%
> 
> **Task:**
> - Spin up a temporary pod using image `busybox:1.28`.
> - Perform an `nslookup` on a service named `payroll` located in the `finance` namespace.
> - Write the fully qualified domain name (FQDN) that resolves to `/opt/payroll-dns.txt` on the jumpbox.

**✅ Solution:**
```bash
# You know the FQDN rule: service.namespace.svc.cluster.local
echo "payroll.finance.svc.cluster.local" > /opt/payroll-dns.txt
```

---

## 🗄️ Domain 3: Storage (10%)

**Q10. PV / PVC Binding**
> **Context:** `kubectl config use-context k8s-store-1`
> **Weight:** 8%
> 
> **Task:**
> - Create a Persistent Volume named `pv-data`. Configure it with `1Gi` capacity, access mode `ReadWriteOnce`, and `hostPath` at `/data/db`.
> - Create a Persistent Volume Claim named `pvc-data` requesting `500Mi` bound to `pv-data`.
> - Create a Pod mounting `pvc-data` to `/var/www/html`.

**✅ Solution:**
```bash
# Get YAML formats from Docs for PV and PVC. Apply them.
kubectl run mount-pod --image=nginx --dry-run=client -o yaml > pod.yaml
# Edit pod.yaml and add volumes and volumeMounts
```

---

**Q11. Multi-Container Shared Storage**
> **Context:** `kubectl config use-context k8s-store-2`
> **Weight:** 6%
> 
> **Task:**
> - Create a Pod named `shared-vol`.
> - Container 1 runs `busybox`, writing standard output to `/var/log/data.txt`.
> - Container 2 runs `busybox`, reading from `/var/log/data.txt`.
> - The files must be shared via an `emptyDir` natively.

**✅ Solution:** Create the pod YAML and configure the `emptyDir: {}` volume, mounting it into both container definitions.

---

## 🛠️ Domain 4: Cluster Architecture (25%)

**Q12. Safe Node Maintenance (Drain)**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 4%
> 
> **Task:**
> The node `worker-1` requires kernel updates.
> - Safely evict all workloads from `worker-1` without causing disruptions to DaemonSets.
> - Ensure no new workloads are scheduled onto it.

**✅ Solution:**
`kubectl drain worker-1 --ignore-daemonsets --force`

---

**Q13. Advanced Kubeadm Upgrade**
> **Context:** `kubectl config use-context k8s-admin-2`
> **Weight:** 10%
> 
> **Task:**
> Upgrade the master node control plane via `kubeadm` to version `v1.35.0`.
> - Do not upgrade the worker nodes.
> - Ensure `kubelet` and `kubectl` on the master are also upgraded.

**✅ Solution:**
```bash
kubectl drain controlplane --ignore-daemonsets
apt-get update && apt install -y kubeadm=1.35.0-00
kubeadm upgrade apply v1.35.0
apt install -y kubelet=1.35.0-00 kubectl=1.35.0-00
systemctl restart kubelet
kubectl uncordon controlplane
```

---

**Q14. ETCD Snapshot & Restore**
> **Context:** `kubectl config use-context k8s-admin-3`
> **Weight:** 12%  *(Guaranteed Question)*
> 
> **Task:**
> - Take an ETCD snapshot and save it to `/opt/backup.db`.
> - Restore the snapshot to the path `/var/lib/etcd-restore`.
> - Reconfigure the control plane to utilize the newly restored path.

**✅ Solution:**
1. Snapshot: `ETCDCTL_API=3 etcdctl snapshot save /opt/backup.db ...`
2. Restore: `ETCDCTL_API=3 etcdctl snapshot restore /opt/backup.db --data-dir=/var/lib/etcd-restore`
3. Route Kubeadm: `vi /etc/kubernetes/manifests/etcd.yaml`, edit hostPath to `/var/lib/etcd-restore`.

---

## 🚑 Domain 5: Troubleshooting (30%)

**Q15. Kubelet Service Failure**
> **Context:** `kubectl config use-context k8s-trouble-1`
> **Weight:** 8%
> 
> **Task:**
> A worker node named `node-abc` is showing as `NotReady`. 
> - Identify the issue preventing the node from joining the cluster.
> - Resolve it so the node returns to `Ready` status.

**✅ Solution:**
`ssh node-abc` -> `systemctl status kubelet` -> `journalctl -u kubelet -f` -> (Fix config typo or disable swap via `swapoff -a`) -> `systemctl restart kubelet`.

---

**Q16. Advanced JSONPath Filter Extraction**
> **Context:** `kubectl config use-context k8s-trouble-2`
> **Weight:** 6%
> 
> **Task:**
> - Output the image versions used by all pods in the `kube-system` namespace.
> - You MUST extract exactly the raw image names using JSONPath.
> - Write the output to `/opt/system-images.txt`.

**✅ Solution:**
`kubectl get pods -n kube-system -o jsonpath='{.items[*].spec.containers[*].image}' > /opt/system-images.txt`

---

**Q17. Resource Sorting**
> **Context:** `kubectl config use-context k8s-trouble-3`
> **Weight:** 4%
> 
> **Task:**
> - Find the node with the highest CPU utilization in the cluster.
> - Write its exact name to the file `/opt/high-cpu.txt`.

**✅ Solution:**
`kubectl top nodes --sort-by=cpu` -> See the top node. -> `echo node01 > /opt/high-cpu.txt`.
