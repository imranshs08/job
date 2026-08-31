# CKA Cheat Sheet: Storage (Volumes, PVs, PVCs)

> **Scope**: Storage & State  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

Containers are ephemeral. If a container crashes, the kubelet restarts it, but all data is lost. K8s solves this using Volumes, Persistent Volumes (PVs), and Persistent Volume Claims (PVCs).

---

## 1. The Pod Volume (EmptyDir & HostPath)

**EmptyDir**: Ephemeral storage. Created when the Pod is assigned to a Node, and deleted forever when the Pod is removed. Used for scratch space or sharing files between containers in the same pod.
**HostPath**: Mounts a file/directory from the host node's filesystem into your Pod. (Dangerous in production, highly likely to be tested on the exam for troubleshooting).

```yaml
  volumes:
  - name: scratch-space
    emptyDir: {}
  - name: host-logs
    hostPath:
      path: /var/log/app
      type: Directory
```

---

## 2. PV and PVC Architecture

For proper persistent storage, K8s decouples storage provisioning from storage consumption.

1. **Persistent Volume (PV)**: A piece of storage in the cluster provisioned by an admin (e.g., an AWS EBS volume or NFS share). (This is the *Supply*).
2. **Persistent Volume Claim (PVC)**: A request for storage by a user/developer. (This is the *Demand*).

When a PVC is created, Kubernetes looks for a PV that matches its requirements (Storage Class, Size, Access Mode) and binds them together.

---

## 3. Storage Classes & Dynamic Provisioning

Instead of admins creating PVs manually, a **StorageClass (SC)** allows dynamic provisioning. When a PVC requests a specific StorageClass, K8s automatically talks to the cloud provider (like AWS), creates the disk, and automatically creates the PV on the fly binding it to the PVC.

```bash
# See default storage classes 
kubectl get sc
```

---

## 4. Writing PV/PVC YAML (Exam Strategy)

There is no imperative command for creating PVs and PVCs. You MUST know where to find the YAML templates in the official Docs during the exam. (Search "Persistent Volumes").

**PVC Example to memorize the structure of:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  # storageClassName: standard # Optional, if omitted it uses cluster default
```

**Mounting it in a Pod:**
```yaml
    volumeMounts:
    - mountPath: "/var/www/html"
      name: mypd
  volumes:
  - name: mypd
    persistentVolumeClaim:
      claimName: my-pvc
```

### Access Modes:
- **ReadWriteOnce (RWO):** Mounted as read-write by a single node. (Most common for DBs).
- **ReadOnlyMany (ROX):** Mounted read-only by many nodes.
- **ReadWriteMany (RWX):** Mounted read-write by many nodes (e.g., NFS).
