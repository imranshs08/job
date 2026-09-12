# 📘 Day-31 | KUBERNETES ARCHITECTURE USING EXAMPLES

## 🎯 The "Why" (Core Concept)
- **Concept:** Kubernetes uses a strict **Client-Server** architecture, completely decoupling the "Brains" (the management overhead) from the "Brawn" (the physical servers running the application). This is fundamentally split into the **Control Plane** (Master) and the **Data Plane** (Worker Nodes).
- **The Analogy:** Think of an automated Amazon Warehouse. The **Control Plane** is the upper-management software determining exactly what boxes need to go where, backed by a massive database. The **Worker Nodes** are the physical floor bots carrying the boxes. The software never carries a box, and the floor bots never make a routing decision.
- **Catastrophic Problem Solved:** It prevents the *Single Point of Failure (SPOF)* trap natively. By decentralizing the workloads and allowing the Control Plane to independently replicate the cluster's state across an armada of Worker Nodes, a complete hardware meltdown of an individual server becomes entirely negligible.

## ⚙️ Architecture & Under the Hood
- **Control Plane: kube-apiserver:** The absolute center of the Kubernetes universe. Every single component—from a user running `kubectl` to a worker node reporting status—physically *must* communicate via the API server. It is the sole component allowed to talk to the database.
- **Control Plane: etcd:** The source of absolute truth. A highly available, strictly consistent Key-Value store holding the entire cluster's configuration and state. If data is not in `etcd`, it does not exist in Kubernetes.
- **Control Plane: kube-scheduler:** The matchmaking accountant. It listens to the API for newly created Pods that have no assigned Node, checks their CPU/Memory requirements against cluster capacity, and technically binds them to the optimal Worker Node.
- **Control Plane: kube-controller-manager:** The enforcer. It runs continuous background loops (like the Node Controller, ReplicaSet Controller) constantly comparing the *actual* state of the cluster against the *desired* state in `etcd`, forcibly fixing any discrepancies.
- **Control Plane: cloud-controller-manager:** The bridge. It allows Kubernetes to natively interact with underlying cloud APIs (Azure, AWS) to provision physical things like external LoadBalancers or Cloud Volumes dynamically.
- **Worker Node: kubelet:** The ship's captain. Running on every Node, the Kubelet receives PodSpecs from the API server and actively ensures the underlying containers are running and healthy.
- **Worker Node: kube-proxy:** The networking engine. It maintains complex OSI Layer-4 network rules (via `iptables` or IPVS) on the host allowing Services to accurately route traffic to the ephemeral Pod IPs.
- **Worker Node: Container Runtime:** The muscular layer beneath Kubernetes (e.g., Containerd, CRI-O, Docker). Kubernetes itself *does not run containers*. The Kubelet commands the runtime to physically unpack the image layer and execute the process.

## 💻 Essential Execution (Commands & YAML)

**1. Verifying Control Plane Architecture Components**
*Because the Control Plane components are frequently deployed as Static Pods natively on the Master Node, you can inspect their real-time state in the `kube-system` namespace.*
```bash
# Verify the health and location of the core Architecture pods
kubectl get pods -n kube-system

# Example Output will expose the engine components:
# etcd-master-node
# kube-apiserver-master-node
# kube-controller-manager-master-node
# kube-scheduler-master-node
```

**2. Example: Inspecting the Kubelet Engine**
*The `kubelet` is uniquely NOT a containerized Pod; it is a raw background system daemon running directly on the Linux node's kernel.*
```bash
# Check the status of the Kubelet daemon directly on the physical Worker Node
systemctl status kubelet
```

## ⚠️ Production Gotchas & Interview Traps
- **The Production Gotcha (ETCD Quorum Collapse):** Because `etcd` requires strict majority consensus (Quorum, mathematically `(N/2)+1`) to vote on cluster changes, running an even number of Master nodes (e.g., 2 or 4) is a production disaster waiting to happen. If you lose one node in a 2-node cluster, you drop to 50% (no majority). `etcd` will instantly lock down into read-only mode, and the cluster cannot auto-heal anything until quorum is restored.
- **The Principal SRE Interview Trap:** *"A developer directly SSHs into a Worker Node and runs `docker kill` on a critical Nginx container. What happens next on an architectural level?"*
  - **The SRE Answer:** "The Container Runtime destroys the process. The local **kubelet** immediately notices the container's death and reports this divergence to the **kube-apiserver**. The API Server updates **etcd**. The **kube-controller-manager**, running a reconciliation loop, detects the actual state dropped below the desired ReplicaSet count. It commands the API Server to create a new Pod. The **kube-scheduler** assigns the Pod to a node, and the new target node's **kubelet** tells its runtime to spin up the replacement container. This all happens in milliseconds."

## 🔍 Debugging (Where to look when it fails)
1. `kubectl get componentstatuses` : (Slightly deprecated but conceptually useful) Outputs the health of the core control plane (`etcd`, `scheduler`, `controller-manager`).
2. `/etc/kubernetes/manifests` : The physical Linux directory on the Master Node where the core Control Plane Static Pod YAMLs live. If you physically edit a file here, the API server pod violently restarts.
3. `/var/log/containers/` : The physical path on the nodes where standard out/err container logs are fundamentally stored on disk.
4. `journalctl -fu kubelet` : Used on a crashing worker node. When a node shows `NotReady` in standard K8s, investigating the Kubelet journalctl trace is strictly mandatory.
5. `kubectl get endpoints` : If `kube-proxy` is misconfigured, Services will lack Endpoints (the actual mapped IP addresses of the backend pods). 

## 📝 10-Second Cheat Sheet
Kubernetes divides its architecture into the **Control Plane** (Brains) and **Data Plane / Worker Nodes** (Muscle). The Control Plane relies on the **kube-apiserver** as the sole gatekeeper strictly reading/writing to the **etcd** key-value database. The **kube-scheduler** intelligently assigns workloads, while the **kube-controller-manager** forcibly maintains the desired state. Down at the Worker Node level, the **kubelet** acts as the local agent instructing the **Container Runtime** to execute the containers, while **kube-proxy** manages the complex `iptables` networking rules. Because `etcd` relies on distributed consensus, Control Planes must always be deployed in mathematically odd clusters (3, 5, 7) to survive extreme hardware failures.
