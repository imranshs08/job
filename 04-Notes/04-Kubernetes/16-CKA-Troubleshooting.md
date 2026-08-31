# CKA Cheat Sheet: Advanced Troubleshooting

> **Scope**: Troubleshooting (30% - Highest Weight)  
> **Tracker Link**: [README.md](README.md)

You must master fixing broken clusters fast. The CKA will deliberately sabotage nodes and components for you to fix.

---

## 1. Evaluating Worker Node Failure

If a node says `NotReady` in `kubectl get nodes`:

1. **Check Node Status/Events:**
   `kubectl describe node <node-name>`
   Look for conditions (MemoryPressure, DiskPressure, PIDPressure). Look at the bottom for raw Events.

2. **SSH into the Node**
   `ssh <node-name>`

3. **Check the Kubelet Process (The most likely culprit!)**
   The Kubelet is a systemd service, NOT a pod. If it crashes, the node goes dark.
   ```bash
   systemctl status kubelet
   journalctl -u kubelet -f    # Tail the kubelet logs to see why it crashed
   ```

4. **Common Kubelet fixes:**
   - Swap was enabled. Kubelet refuses to run if swap is on. (`swapoff -a`)
   - Incorrect cert paths in `/var/lib/kubelet/config.yaml`.
   - After fixing, always run: `systemctl restart kubelet`

---

## 2. Control Plane Component Failure

If you can't run `kubectl` commands, or pods stay `Pending` despite having free nodes, a Control Plane component is dead.

1. **Kube-API Server is down:** `kubectl` won't respond at all (`The connection to the server was refused`).
2. **Kube-Scheduler is down:** Pods stay `Pending` forever in a healthy cluster.
3. **Kube-Controller-Manager is down:** ReplicaSets don't replace dead pods.

**How to Fix Them:**
Control plane components run as Static Pods on the Master Node.
1. `cd /etc/kubernetes/manifests`
2. Look for typos in `kube-apiserver.yaml`, `kube-scheduler.yaml`, or `kube-controller-manager.yaml`. 
3. If a command argument (like `--kubeconfig`) points to the wrong file, the pod instantly CrashLoopBackOffs. Fix the YAML, and Kubelet automatically restarts the static pod.

---

## 3. Network/CNI Failure

If pods are running but Services cannot reach them, or internal DNS is failing across the cluster.
1. Did you install a CNI? A cluster won't assign IP addresses (pods stay `Pending` or `ContainerCreating`) if the CNI plugin (Weave, Calico, Flannel) is missing.
2. Check CNI binaries: `ls /opt/cni/bin`
3. Check CNI configuration: `cat /etc/cni/net.d/`

---

## 4. Useful Sysadmin Commands

```bash
# See what is listening on a port (e.g., is something blocking port 6443?)
netstat -tulpn | grep 6443
# OR
ss -tulpn | grep 6443

# Check system logs for containerd (the container runtime)
systemctl status containerd
journalctl -u containerd
```
