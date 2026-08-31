# CKA Cheat Sheet: ETCD Backup & Restore

> **Scope**: Cluster Architecture (25%)  
> **Tracker Link**: [README.md](README.md)

ETCD is the brain of the Kubernetes cluster. It is a highly-available key-value store that holds the entire state of the cluster (all pods, deployments, secrets, etc.). If ETCD dies and you have no backup, the cluster is gone.

---

## 1. Prerequisites for `etcdctl`

The CKA exam will ask you to take a snapshot of ETCD and restore it. You will usually have to SSH into the master node (Control Plane) to do this.

ETCD uses mTLS for authentication. You **must** provide the 3 certificate files to `etcdctl` for it to work.
You can find where these certificates live by looking at the ETCD static pod manifest:
`cat /etc/kubernetes/manifests/etcd.yaml`

---

## 2. Taking a Snapshot (Backup)

```bash
# Variables (Find these paths in /etc/kubernetes/manifests/etcd.yaml)
ETCD_ENDPOINT="127.0.0.1:2379"
CACERT="/etc/kubernetes/pki/etcd/ca.crt"
CERT="/etc/kubernetes/pki/etcd/server.crt"
KEY="/etc/kubernetes/pki/etcd/server.key"

# Take the Snapshot (Exam Time-Saver command)
ETCDCTL_API=3 etcdctl snapshot save /opt/snapshot-pre-boot.db \
  --endpoints=${ETCD_ENDPOINT} \
  --cacert=${CACERT} \
  --cert=${CERT} \
  --key=${KEY}
```
*Verify it worked:*
`ETCDCTL_API=3 etcdctl snapshot status /opt/snapshot-pre-boot.db -w table`

---

## 3. Restoring from a Snapshot

⚠️ **CRITICAL:** Do *not* restore over the running ETCD data directory. You must restore to a *new* folder, and then edit the ETCD static pod to point to the new folder.

```bash
# 1. Restore the snapshot into a NEW directory
ETCDCTL_API=3 etcdctl snapshot restore /opt/snapshot-pre-boot.db \
  --data-dir=/var/lib/etcd-backup

# 2. Modify the ETCD Static Pod to use the new directory
# Open the manifest in vi
vi /etc/kubernetes/manifests/etcd.yaml

# 3. Inside the YAML, change the hostPath for the etcd-data volume:
  volumes:
  - hostPath:
      path: /var/lib/etcd-backup # <--- Changed this from /var/lib/etcd
      type: DirectoryOrCreate
    name: etcd-data

# 4. Save and exit. 
# Kubelet will auto-detect the manifest change and restart the ETCD pod.
```
