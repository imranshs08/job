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

---

## 🌩️ PART 2: KodeKloud Mock Exam Classics

*KodeKloud is renowned for having the most accurate mock exams. These scenarios are ripped straight from the patterns seen in KodeKloud Mock 1, 2, and 3.*

**Q18. Broken Kubeconfig (KodeKloud Classic)**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 8%
> 
> **Task:**
> The kubeconfig file located at `/root/.kube/config` is misconfigured. You cannot connect to the cluster.
> - Identify the issue within the kubeconfig file and fix it so `kubectl` commands work again.

**✅ Solution:**
1. Run `cat /root/.kube/config`. Look at the `server: https://192.168.1.10:6433` line.
2. The default port for the Kube-API server is `6443`, not `6433` (a very common KodeKloud trick).
3. `vi /root/.kube/config`, change the port to `6443`, save and quit.
4. Test with `kubectl get nodes`.

---

**Q19. Extracting Internal Node IPs via JSONPath**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 5%
> 
> **Task:**
> - Find the `InternalIP` of node `node01`.
> - Extract ONLY the IP address using JSONPath.
> - Write this IP address to the file `/opt/node01_ip.txt`.

**✅ Solution:**
```bash
# JSONPath to dig into the addresses array and extract the InternalIP
kubectl get node node01 -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}' > /opt/node01_ip.txt
```

---

**Q20. Deploying with a specific ServiceAccount**
> **Context:** `kubectl config use-context k8s-rbac-1`
> **Weight:** 6%
> 
> **Task:**
> - Create a ServiceAccount named `web-sa` in the `default` namespace.
> - Create a Pod named `web-pod` using image `nginx`.
> - The Pod MUST use the `web-sa` ServiceAccount instead of the `default` ServiceAccount.

**✅ Solution:**
```bash
kubectl create sa web-sa
kubectl run web-pod --image=nginx --dry-run=client -o yaml > pod.yaml
# Edit pod.yaml and add 'serviceAccountName: web-sa' under spec:
# spec:
#   serviceAccountName: web-sa
#   containers:
kubectl apply -f pod.yaml
```

---

**Q21. PersistentVolume Binding by Label (Mock 2 Variant)**
> **Context:** `kubectl config use-context k8s-store-1`
> **Weight:** 7%
> 
> **Task:**
> A PersistentVolume named `pv-secure` already exists in the cluster. It has the label `storageTier: gold`.
> - Create a Persistent Volume Claim named `pvc-secure` that requests `500Mi`.
> - Do NOT use a StorageClass.
> - Use a `selector` in your PVC to ensure it binds EXACTLY to `pv-secure` via the `storageTier: gold` label.

**✅ Solution:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-secure
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
  selector:
    matchLabels:
      storageTier: gold
```
*Apply it and verify `kubectl get pvc` displays `Bound` immediately!*

---

**Q22. CoreDNS Service Resolution Test**
> **Context:** `kubectl config use-context k8s-net-4`
> **Weight:** 4%
> 
> **Task:**
> - A deployment `db-backend` and its ClusterIP service `db-service` exist in the `backend` namespace.
> - Spin up a temporary pod using `busybox:1.28` in the `default` namespace.
> - Perform an `nslookup` on the `db-service` from the temporary pod.
> - Record the IP address returned by the DNS query in `/opt/db-ip.txt`.

**✅ Solution:**
```bash
# Since the pod is in default, and service is in backend, use the FQDN!
kubectl run temp-test --image=busybox:1.28 -it --rm --restart=Never -- nslookup db-service.backend.svc.cluster.local > /opt/db-ip.txt
# (Trim the txt file to leave just the IP address if you piped it directly!)
```

---

## 🏗️ PART 3: The Expanding Workloads Collection

**Q23. Custom Resource Definitions (CRDs)**
> **Context:** `kubectl config use-context k8s-admin-2`
> **Weight:** 2%
> 
> **Task:**
> Find the names of all Custom Resource Definitions (CRDs) available in the cluster and write them to `/opt/crds.txt`.

**✅ Solution:**
`kubectl get crds -o name > /opt/crds.txt`

---

**Q24. Rolling Updates & History**
> **Context:** `kubectl config use-context k8s-web-1`
> **Weight:** 4%
> 
> **Task:**
> A deployment `web-app` exists in `prod`. 
> Change its image to `nginx:1.21.1`. Record it. Then undo the rollout back to the previous version.

**✅ Solution:**
```bash
kubectl set image deployment/web-app nginx=nginx:1.21.1 -n prod --record
kubectl rollout undo deployment/web-app -n prod
```

---

**Q25. Deployment Scaling**
> **Context:** `kubectl config use-context k8s-web-2`
> **Weight:** 2%
> 
> **Task:**
> Scale the `payment-gateway` deployment in the `finance` namespace to `6` replicas.

**✅ Solution:**
`kubectl scale deployment payment-gateway -n finance --replicas=6`

---

**Q26. Manual Pod Creation**
> **Context:** `kubectl config use-context k8s-sched-1`
> **Weight:** 3%
> 
> **Task:**
> Create a pod named `manual-job` running image `redis:alpine` with CPU memory limits set to `64Mi`.

**✅ Solution:**
`kubectl run manual-job --image=redis:alpine --limits=memory=64Mi`

---

**Q27. Taint Removal**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 3%
> 
> **Task:**
> Node `worker-2` has a taint `app=database:NoExecute`. Remove this taint.

**✅ Solution:**
`kubectl taint node worker-2 app=database:NoExecute-`

---

**Q28. Multiple Environment Variables**
> **Context:** `kubectl config use-context k8s-dev-1`
> **Weight:** 4%
> 
> **Task:**
> Create a pod `env-pod` running `nginx`. Pass the environment variable `APP_ENV=prod` and `RATE_LIMIT=100` into it natively.

**✅ Solution:**
`kubectl run env-pod --image=nginx --env=APP_ENV=prod --env=RATE_LIMIT=100`

---

**Q29. InitContainers File Creation**
> **Context:** `kubectl config use-context k8s-dev-1`
> **Weight:** 6%
> 
> **Task:**
> Deploy a pod `setup-pod` (image `nginx`). Add an initContainer (image `busybox`) that creates an empty file at `/work-dir/ready.txt`. 

**✅ Solution:** Sub the pod. Add the `initContainers:` block overriding the command to `touch /work-dir/ready.txt`.

---

**Q30. Multi-container Sidecar pattern**
> **Context:** `kubectl config use-context k8s-log-1`
> **Weight:** 6%
> 
> **Task:**
> Deploy a pod `multi-log`. Container 1 (nginx). Container 2 (busybox reading nginx logs). No volume required.

**✅ Solution:** Stub with `kubectl run... > pod.yaml`. Duplicate the container block inside the file.

---

**Q31. Multi-Port Service**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 4%
> 
> **Task:**
> Expose pod `dual-app` on two ports internally: `8080` to target `80`, and `9090` to target `443`.

**✅ Solution:** Export to YAML `kubectl expose pod ... --dry-run=client -o yaml` and manually add the second port block.

---

**Q32. Ingress Fan-Out Routing**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 8%
> 
> **Task:**
> Create an Ingress named `web-ingress`. 
> Route `/video` to service `video-svc` on port 80.
> Route `/audio` to service `audio-svc` on port 8080.

**✅ Solution:** Use `kubectl create ingress web-ingress --rule="/video*=video-svc:80" --rule="/audio*=audio-svc:8080"` (Or search K8s docs for Ingress YAML).

---

**Q33. Network Policy: Allow Egress**
> **Context:** `kubectl config use-context k8s-sec-1`
> **Weight:** 7%
> 
> **Task:**
> Create a network policy `allow-dns` in the `backend` namespace allowing egress ONLY to port 53 (UDP/TCP).

**✅ Solution:** Search Network Policy in docs. Add an `egress:` block with `ports:` 53.

---

**Q34. ExternalName Service**
> **Context:** `kubectl config use-context k8s-net-2`
> **Weight:** 3%
> 
> **Task:**
> Create a service `google-svc` that resolves to `google.com`.

**✅ Solution:** 
`kubectl create service externalname google-svc --external-name google.com`

---

**Q35. Service Endpoint Inspection**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 3%
> 
> **Task:**
> Output the endpoint IPs of the service `db-svc` to `/opt/db-endpoints.txt`.

**✅ Solution:**
`kubectl get endpoints db-svc -o jsonpath='{.subsets[*].addresses[*].ip}' > /opt/db-endpoints.txt`
*(Or manually copy from `kubectl get ep db-svc`).*

---

**Q36. ConfigMap Volumes**
> **Context:** `kubectl config use-context k8s-store-1`
> **Weight:** 5%
> 
> **Task:**
> Create a ConfigMap `app-vars` from literal `ENV=dev`. Mount it inside a pod `cfg-pod` at `/app/config`.

**✅ Solution:**
Create CM imperatively. Sub pod to YAML. Add `volumes: - configMap: name: app-vars` and `volumeMounts`.

---

**Q37. Persistent Volume Reclaim Policy**
> **Context:** `kubectl config use-context k8s-store-2`
> **Weight:** 3%
> 
> **Task:**
> Change the reclaim policy of the PV `pv-legacy` to `Retain`.

**✅ Solution:**
`kubectl patch pv pv-legacy -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'`

---

**Q38. Sorting PVs by Capacity**
> **Context:** `kubectl config use-context k8s-store-3`
> **Weight:** 4%
> 
> **Task:**
> Output the names of all Persistent Volumes sorted by their storage capacity to `/opt/pvs.txt`.

**✅ Solution:**
`kubectl get pv --sort-by=.spec.capacity.storage -o name > /opt/pvs.txt`

---

**Q39. Secret Configuration**
> **Context:** `kubectl config use-context k8s-sec-2`
> **Weight:** 4%
> 
> **Task:**
> Create a Secret `api-key` containing `key=123AB`. Inject it as an environmental variable `API_KEY` into pod `api-pod`.

**✅ Solution:** Create secret imperatively. Edit pod YAML: `valueFrom: secretKeyRef ...`

---

**Q40. StorageClass Default Verification**
> **Context:** `kubectl config use-context k8s-store-1`
> **Weight:** 2%
> 
> **Task:**
> Determine which StorageClass is marked as default in the cluster and write its name to `/opt/default-sc.txt`.

**✅ Solution:**
`kubectl get sc` (Look for the one with `(default)`).

---

## 🛠️ PART 4: Deep Troubleshooting & Architecture

**Q41. Node Uncordoning**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 2%
> 
> **Task:**
> Node `worker-2` is marked as `SchedulingDisabled`. Fix it so it accepts pods again.

**✅ Solution:**
`kubectl uncordon worker-2`

---

**Q42. Worker Node Upgrade Preparation**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 4%
> 
> **Task:**
> Drain `worker-2` safely for an OS reboot. Ignore daemonsets and force eviction.

**✅ Solution:**
`kubectl drain worker-2 --ignore-daemonsets --force`

---

**Q43. Kubeadm Worker Upgrade**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 6%
> 
> **Task:**
> Upgrade `kubeadm` on `worker-2` to `1.35.0-00`, then upgrade the local node configuration.

**✅ Solution:**
SSH into node. `apt install kubeadm=1.35.0-00 && kubeadm upgrade node`.

---

**Q44. Static Pod Creation**
> **Context:** `kubectl config use-context k8s-admin-2`
> **Weight:** 5%
> 
> **Task:**
> Create a static pod named `static-web` running `nginx:alpine` on the master node without using the API server.

**✅ Solution:**
SSH into master. `kubectl run static-web --image=nginx:alpine --dry-run=client -o yaml > /etc/kubernetes/manifests/static-web.yaml`

---

**Q45. Role Creation**
> **Context:** `kubectl config use-context k8s-rbac-2`
> **Weight:** 4%
> 
> **Task:**
> Create a Role `pod-reader` in namespace `development` that can `get, list, watch` pods.

**✅ Solution:**
`kubectl create role pod-reader -n development --verb=get,list,watch --resource=pods`

---

**Q46. Role Binding Generation**
> **Context:** `kubectl config use-context k8s-rbac-2`
> **Weight:** 4%
> 
> **Task:**
> Bind the `pod-reader` Role to the ServiceAccount `developer` in the `development` namespace.

**✅ Solution:**
`kubectl create rolebinding pod-reader-bind -n development --role=pod-reader --serviceaccount=development:developer`

---

**Q47. Event Output Parsing**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 4%
> 
> **Task:**
> Output all cluster events sorted by creation timestamp into `/opt/events.txt`.

**✅ Solution:**
`kubectl get events -A --sort-by=.metadata.creationTimestamp > /opt/events.txt`

---

**Q48. CoreDNS IP Extraction**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 3%
> 
> **Task:**
> Find the ClusterIP address of the `kube-dns` service and save it to `/opt/dns-ip.txt`.

**✅ Solution:**
`kubectl get svc -n kube-system kube-dns -o jsonpath='{.spec.clusterIP}' > /opt/dns-ip.txt`

---

**Q49. Check DaemonSet Status**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 3%
> 
> **Task:**
> Identify which DaemonSet is running in the `kube-system` namespace to provide networking.

**✅ Solution:**
`kubectl get daemonsets -n kube-system` (Likely kube-proxy, calico, or weave).

---

**Q50. Node Capacity Filtering**
> **Context:** `kubectl config use-context k8s-admin-1`
> **Weight:** 4%
> 
> **Task:**
> Out of all nodes, find the one with the most CPU capacity. Write its name to `/opt/max-cpu.txt`.

**✅ Solution:**
`kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.capacity.cpu}{"\n"}{end}'` -> Pick the biggest one.

---

**Q51. HostNetwork Pods**
> **Context:** `kubectl config use-context k8s-net-5`
> **Weight:** 4%
> 
> **Task:**
> Create a pod `host-net` running `nginx`. It must bypass the CNI and bind directly to the worker node's network interface.

**✅ Solution:** Add `hostNetwork: true` to the pod spec.

---

**Q52. ETCD Alternative Restore**
> **Context:** `kubectl config use-context k8s-admin-3`
> **Weight:** 10%
> 
> **Task:**
> Restore the snapshot located at `/opt/old-snap.db` to `/var/lib/etcd-alt`. Update the ETCD static pod to point to it.

**✅ Solution:**
`ETCDCTL_API=3 etcdctl snapshot restore /opt/old-snap.db --data-dir=/var/lib/etcd-alt`. Then edit `/etc/kubernetes/manifests/etcd.yaml`.

---

**Q53. Forced Pod Deletion**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 2%
> 
> **Task:**
> A pod `stuck-pod` is trapped in the `Terminating` state forever. Delete it forcefully immediately.

**✅ Solution:**
`kubectl delete pod stuck-pod --force --grace-period=0`

---

**Q54. Liveness Probe Configuration**
> **Context:** `kubectl config use-context k8s-web-3`
> **Weight:** 6%
> 
> **Task:**
> Add an HTTP GET Liveness probe to the `app` container in the `web-pod` YAML. It should hit port 80 at `/healthz`.

**✅ Solution:** Edit pod YAML, add:
```yaml
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
```

---

**Q55. Container Runtime Logs**
> **Context:** `kubectl config use-context k8s-trouble-1`
> **Weight:** 4%
> 
> **Task:**
> The `containerd` runtime on node `worker-1` is acting up. Extract the last 20 lines of its systemd journal.

**✅ Solution:**
`ssh worker-1`, then `journalctl -u containerd -n 20`

---

**Q56. CNI Binaries Inspection**
> **Context:** `kubectl config use-context k8s-net-1`
> **Weight:** 2%
> 
> **Task:**
> Find the directory where CNI configuration files are stored on the master node.

**✅ Solution:** Look in `/etc/cni/net.d/`.

---

**Q57. Testing Role Permissions**
> **Context:** `kubectl config use-context k8s-rbac-1`
> **Weight:** 3%
> 
> **Task:**
> Verify without authenticating if the ServiceAccount `test-user` in namespace `qa` can delete configmaps.

**✅ Solution:**
`kubectl auth can-i delete configmaps --as=system:serviceaccount:qa:test-user -n qa`

---

**Q58. Finding specific Annotations**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 3%
> 
> **Task:**
> Output the annotations of the pod `nginx-ann` to a file `/opt/ann.txt`.

**✅ Solution:**
`kubectl get pod nginx-ann -o jsonpath='{.metadata.annotations}' > /opt/ann.txt`

---

**Q59. Port-Forwarding (Internal Testing)**
> **Context:** `kubectl config use-context k8s-debug-1`
> **Weight:** 2%
> 
> **Task:**
> The `db` pod doesn't have a service. Forward traffic from your local terminal port `8080` to the pod's port `5432`.

**✅ Solution:**
`kubectl port-forward pod/db 8080:5432`

---

**Q60. Final Boss: Control Plane Total Failure**
> **Context:** `kubectl config use-context k8s-admin-x`
> **Weight:** 15%
> 
> **Task:**
> Cluster is completely down. `kubectl` says connection refused.
> Identify the failed static pod and return the cluster to a healthy state.

**✅ Solution:**
1. Check `systemctl status kubelet`. If dead, start it.
2. If `kubelet` is running, `cd /etc/kubernetes/manifests`.
3. Read the logs using the container runtime directly! `crictl ps -a` -> `crictl logs <id>`.
4. Locate the YAML typo (usually `kube-apiserver.yaml` has a misspelled flag like `--etcd-servers=htts://...`). Fix the typo.

---
*End of CKA Mega Bank.*
