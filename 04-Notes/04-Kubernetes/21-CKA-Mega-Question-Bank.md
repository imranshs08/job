# 🏆 CKA Mega Question Bank (60 Real Exam Scenarios)

> **Scope:** Intense repetition for CKA Muscle Memory.  
> **Note:** The actual CKA exam contains 15-20 questions. These 60 scenarios represent almost every possible variant of those questions you will encounter on the internet and in past exams.

---

## 🛠️ Domain 1: Workloads & Scheduling (15 Questions)

**Q1.** Create a pod named `nginx-pod` using image `nginx:alpine` in namespace `web` with a CPU request of `200m`.
**✅ Solution:** 
`kubectl run nginx-pod --image=nginx:alpine -n web --requests=cpu=200m`

**Q2.** Create a deployment named `redis-deploy` with 3 replicas using image `redis:6`.
**✅ Solution:**
`kubectl create deployment redis-deploy --image=redis:6 --replicas=3`

**Q3.** Scale the deployment `redis-deploy` to 5 replicas.
**✅ Solution:**
`kubectl scale deployment redis-deploy --replicas=5`

**Q4.** Perform a rolling update on `redis-deploy` changing the image to `redis:7`.
**✅ Solution:**
`kubectl set image deployment/redis-deploy redis=redis:7 --record`

**Q5.** Undo the rolling update on `redis-deploy` back to the previous version.
**✅ Solution:**
`kubectl rollout undo deployment redis-deploy`

**Q6.** Taint node `worker-2` with `env=prod:NoSchedule`.
**✅ Solution:**
`kubectl taint node worker-2 env=prod:NoSchedule`

**Q7.** Create a pod `toleration-pod` that can run on `worker-2` with the taint `env=prod:NoSchedule`.
**✅ Solution:** Generate stub `kubectl run ... > pod.yaml` and add:
```yaml
  tolerations:
  - key: "env"
    operator: "Equal"
    value: "prod"
    effect: "NoSchedule"
```

**Q8.** Label node `worker-1` with `diskType=ssd`.
**✅ Solution:**
`kubectl label node worker-1 diskType=ssd`

**Q9.** Deploy a pod `ssd-pod` that MUST run on nodes labeled `diskType=ssd`.
**✅ Solution:** Add `nodeSelector` to `pod.yaml`:
```yaml
  nodeSelector:
    diskType: ssd
```

**Q10.** Check how many pods are running in the `kube-system` namespace.
**✅ Solution:**
`kubectl get pods -n kube-system | wc -l` (Subtract 1 for the header).

**Q11.** Find the node with the highest CPU utilization and write it to `/opt/high.txt`.
**✅ Solution:**
`kubectl top nodes --sort-by=cpu | head -n 2 > /opt/high.txt`

**Q12.** Schedule a pod to forcefully run on `master-node` bypassing the scheduler.
**✅ Solution:** Add `nodeName: master-node` to the pod spec.

**Q13.** Create a DaemonSet named `fluentd` running image `fluentd`.
**✅ Solution:** Create a Deployment YAML, change `kind: Deployment` to `kind: DaemonSet`, delete `replicas` and `strategy` blocks.

**Q14.** Create a static pod named `static-web` on the master node running `nginx`.
**✅ Solution:**
`kubectl run static-web --image=nginx --dry-run=client -o yaml > /etc/kubernetes/manifests/static-web.yaml`

**Q15.** Output the image version used by all pods in the `kube-system` namespace using JSONPath.
**✅ Solution:**
`kubectl get pods -n kube-system -o jsonpath='{.items[*].spec.containers[*].image}'`

---

## 🚦 Domain 2: Services & Networking (15 Questions)

**Q16.** Expose deployment `frontend` inside the cluster on port 80. Name it `front-svc`.
**✅ Solution:**
`kubectl expose deployment frontend --name=front-svc --port=80 --type=ClusterIP`

**Q17.** Expose a pod named `db` externally on NodePort 32000.
**✅ Solution:**
`kubectl expose pod db --name=db-svc --port=5432 --type=NodePort` -> `kubectl edit svc db-svc` -> Change nodePort to 32000.

**Q18.** Create a NetworkPolicy named `allow-port-from-namespace`. Allow traffic to pods labeled `role=db` on port `3306` ONLY from namespace `web`.
**✅ Solution:** Search `NetworkPolicy` in docs. Add `namespaceSelector` under `from`.

**Q19.** Deny all egress traffic from namespace `restricted`.
**✅ Solution:** Create NetworkPolicy with empty `egress: []` block.

**Q20.** Find the DNS record of the service `app-svc` in the `dev` namespace.
**✅ Solution:**
`app-svc.dev.svc.cluster.local`

**Q21.** Spin up a `busybox:1.28` pod to `nslookup` a service named `payroll`.
**✅ Solution:**
`kubectl run test --image=busybox:1.28 -it --rm --restart=Never -- nslookup payroll`

**Q22.** Update a Service named `backend-svc` to select pods with label `tier=backend-v2`.
**✅ Solution:**
`kubectl edit svc backend-svc` -> Edit the `selector` block.

**Q23.** Create an Ingress resource `app-ingress` routing `/pay` to `pay-svc` and `/hr` to `hr-svc`.
**✅ Solution:** Search `Ingress` in docs and use the multi-path template.

**Q24.** Find the Cluster IP of the `kube-dns` service.
**✅ Solution:**
`kubectl get svc -n kube-system | grep kube-dns`

**Q25.** List all Services across all namespaces sorted by creation timestamp.
**✅ Solution:**
`kubectl get svc -A --sort-by=.metadata.creationTimestamp`

**Q26.** Map an external domain `google.com` to an internal service named `external-link`.
**✅ Solution:** Create a Service of type `ExternalName` with `externalName: google.com`.

**Q27.** Output the endpoint IP addresses assigned to the `my-web` service.
**✅ Solution:**
`kubectl get endpoints my-web`

**Q28.** What CNI plugin is currently installed in the cluster?
**✅ Solution:** Look in `/etc/cni/net.d/` or `kubectl get pods -n kube-system` (look for calico, weave, flannel).

**Q29.** A pod is stuck in `ContainerCreating`. Identify if it's a network issue.
**✅ Solution:**
`kubectl describe pod <name>` -> Look at the bottom events for "failed to set up sandbox container" or "networkPlugin cni failed".

**Q30.** Create a pod named `net-host` that uses the host's physical network namespace.
**✅ Solution:** Add `hostNetwork: true` to the pod spec.

---

## 🗄️ Domain 3: Storage (10 Questions)

**Q31.** Create a PV named `pv-data` (1Gi, ReadWriteOnce, hostPath `/data/db`).
**✅ Solution:** Search `PersistentVolume` in docs. Modify capacities and hostPath.

**Q32.** Create a PVC `pvc-data` requesting `500Mi` bound to `pv-data`.
**✅ Solution:** Search `PersistentVolumeClaim`. Ensure access modes match.

**Q33.** View the status of PVC `pvc-data` and verify it says `Bound`.
**✅ Solution:**
`kubectl get pvc pvc-data`

**Q34.** Create a pod mounting `pvc-data` to `/var/www/html`.
**✅ Solution:** Use docs to add `volumeMounts` and `volumes` (persistentVolumeClaim claimName).

**Q35.** Create an `emptyDir` volume natively shared by two containers in the same pod.
**✅ Solution:** Add `volumes: - name: vol emptyDir: {}`.

**Q36.** Change the re-claim policy of PV `pv-data` to `Retain`.
**✅ Solution:**
`kubectl patch pv pv-data -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'`

**Q37.** Create a StorageClass named `fast-disk` with provisioner `kubernetes.io/gce-pd`.
**✅ Solution:** Search `StorageClass` in docs.

**Q38.** Find all PVs sorted by capacity.
**✅ Solution:**
`kubectl get pv --sort-by=.spec.capacity.storage`

**Q39.** Why is a PVC stuck in `Pending`?
**✅ Solution:** `kubectl describe pvc`. Usually no PV matches the request size, access mode, or StorageClass.

**Q40.** Mount a ConfigMap named `app-config` as a volume inside a pod at `/etc/config`.
**✅ Solution:** Search `ConfigMap Volume` in docs.

---

## 🛠️ Domain 4: Cluster Architecture & Upgrades (10 Questions)

**Q41.** Drain node `worker-1` safely for maintenance.
**✅ Solution:**
`kubectl drain worker-1 --ignore-daemonsets --force`

**Q42.** Uncordon node `worker-1` to allow pods back on.
**✅ Solution:**
`kubectl uncordon worker-1`

**Q43.** Upgrade the master node control plane via `kubeadm` to the next minor version.
**✅ Solution:** `kubeadm upgrade plan`, `kubeadm upgrade apply v1.x.y`.

**Q44.** Upgrade `kubelet` and `kubectl` on a worker node.
**✅ Solution:** `apt-get install -y kubelet=x.y.z`, `systemctl restart kubelet`.

**Q45.** Take an ETCD snapshot to `/opt/backup.db`.
**✅ Solution:**
`ETCDCTL_API=3 etcdctl snapshot save /opt/backup.db --endpoints=... --cacert=... --cert=... --key=...`

**Q46.** Restore an ETCD snapshot from `/opt/backup.db` to `/var/lib/etcd-restore`.
**✅ Solution:**
`ETCDCTL_API=3 etcdctl snapshot restore /opt/backup.db --data-dir=/var/lib/etcd-restore`.

**Q47.** Update the ETCD static pod to point to the restored backup directory.
**✅ Solution:** `vi /etc/kubernetes/manifests/etcd.yaml`, update `hostPath` block.

**Q48.** Create a ServiceAccount named `backup-bot`.
**✅ Solution:** `kubectl create sa backup-bot`

**Q49.** Create a Role named `pod-reader` to get, list pods.
**✅ Solution:** `kubectl create role pod-reader --verb=get,list --resource=pods`

**Q50.** Bind `backup-bot` to `pod-reader`.
**✅ Solution:** `kubectl create rolebinding bot-bind --role=pod-reader --serviceaccount=default:backup-bot`

---

## 🚑 Domain 5: Troubleshooting (10 Questions)

**Q51.** A worker node is `NotReady`. How do you find out why?
**✅ Solution:** `kubectl describe node`, check Conditions. SSH into node.

**Q52.** The `kubelet` service is stopped. Start it and check logs.
**✅ Solution:** `systemctl enable kubelet && systemctl start kubelet && journalctl -u kubelet -f`

**Q53.** A pod is in `CrashLoopBackOff`. How do you find the exact application error?
**✅ Solution:** `kubectl logs <pod-name>` (or `--previous` if it just restarted).

**Q54.** A pod is deleted but stays stuck in `Terminating`. Force delete it.
**✅ Solution:** `kubectl delete pod <name> --force --grace-period=0`

**Q55.** Check the logs of the `kube-apiserver` static pod directly from the master node.
**✅ Solution:** `cat /var/log/pods/kube-system_kube-apiserver.../kube-apiserver/0.log` OR use `crictl logs`.

**Q56.** A service `web-svc` is not routing to its underlying pods.
**✅ Solution:** Check endpoints: `kubectl get ep web-svc`. If empty, the Service `selector` labels do not match the Pod labels.

**Q57.** Find out what process is blocking port 6443 on the master node.
**✅ Solution:** `netstat -tulpn | grep 6443`

**Q58.** Check if `kube-proxy` is running as a DaemonSet.
**✅ Solution:** `kubectl get daemonsets -n kube-system`

**Q59.** Output all events in the cluster to see recently killed pods.
**✅ Solution:** `kubectl get events --sort-by=.metadata.creationTimestamp`

**Q60.** The pod is failing a Liveness Probe but the application logs look fine.
**✅ Solution:** `kubectl describe pod`. Look at the `Liveness probe failed` event. It might be hitting the wrong port or path (e.g., `/health` instead of `/healthz`).
