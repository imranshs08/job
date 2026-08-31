# CKA Cheat Sheet: Kubeadm Upgrades

> **Scope**: Cluster Architecture (25%)  
> **Tracker Link**: [README.md](README.md)

On the exam, you will likely be asked to upgrade a cluster from one version (e.g., `v1.34.0`) to another (`v1.35.0`) using `kubeadm`.

**Golden Rule of Kubeadm Upgrades:**
1. Upgrade the Primary Control Plane node first.
2. Upgrade the Worker nodes second.
3. Kubeadm does **not** upgrade `kubelet` or `kubectl`. You must upgrade them using `apt` / `yum` manually.

---

## Part 1: Upgrading the Control Plane (Master Node)

```bash
# 1. Drain the Master Node (Evict all pods gracefully)
kubectl drain controlplane --ignore-daemonsets

# 2. Update the OS package manager list and find the exact version requested
apt update
apt-cache madison kubeadm # (Look for the exact version string, e.g. 1.35.0-1.1)

# 3. Upgrade kubeadm itself
apt-mark unhold kubeadm
apt-get install -y kubeadm='1.35.0-1.2' # Example
apt-mark hold kubeadm

# 4. Verify the upgrade plan
kubeadm upgrade plan

# 5. Apply the upgrade (Wait for it to say SUCCESS)
kubeadm upgrade apply v1.35.0

# 6. Upgrade kubelet and kubectl
apt-mark unhold kubelet kubectl
apt-get install -y kubelet='1.35.0-1.2' kubectl='1.35.0-1.2'
apt-mark hold kubelet kubectl

# 7. Restart kubelet
systemctl daemon-reload
systemctl restart kubelet

# 8. Uncordon the node (allow pods to be scheduled again)
kubectl uncordon controlplane
```

---

## Part 2: Upgrading a Worker Node

The process is almost identical, but you run `upgrade node` instead of `upgrade apply`.

```bash
# 1. From the CONTROL PLANE, drain the worker node
kubectl drain node01 --ignore-daemonsets --force

# 2. SSH into the worker node
ssh node01

# 3. Upgrade kubeadm on the worker
apt-mark unhold kubeadm
apt-get install -y kubeadm='1.35.0-1.2'
apt-mark hold kubeadm

# 4. Apply the upgrade to the local node config
kubeadm upgrade node

# 5. Upgrade kubelet and kubectl on the worker
apt-mark unhold kubelet kubectl
apt-get install -y kubelet='1.35.0-1.2' kubectl='1.35.0-1.2'
apt-mark hold kubelet kubectl
systemctl daemon-reload
systemctl restart kubelet

# 6. Exit SSH, go back to Control Plane, and uncordon
exit
kubectl uncordon node01
```
