# 📘 KUBERNETES INTERVIEW QUESTIONS PART-1 | What's Your Score ?

## 🎯 The "Why" (Core Concept)
- Kubernetes is a **container orchestration platform** that automates the deployment, scaling, and management of containerized workloads. 
- *Analogy:* If Docker is the raw engine of a car, Kubernetes is the entire self-driving fleet management system determining which car goes where, routing traffic to them, and restarting them if they crash.
- **Catastrophic Problem Solved:** It eliminates the operational nightmare of manually managing thousands of individual containers across a massive distributed infrastructure, preventing localized node failures from causing global application downtime.

## ⚙️ Architecture & Under the Hood
- **Control Plane (The Brain):** Manages the cluster state and worker nodes.
  - **API Server:** The absolute gateway. Every single `kubectl` command or internal component talks *only* to the API Server.
  - **etcd:** The highly available, distributed key-value store holding the entire cluster state. If etcd dies, the cluster suffers amnesia.
  - **kube-scheduler:** Watches for newly created Pods with no assigned node, mathematically scoring nodes based on resource limits and taints to assign them securely.
  - **kube-controller-manager:** Runs the core control loops (Node controller, ReplicaSet controller) constantly reconciling desired state vs. actual state.
- **Worker Nodes (The Muscle):** The actual machines executing the workloads.
  - **kubelet:** The node agent. It registers the node with the API server and physically instructs the container runtime (e.g., containerd) to start/stop the Pods.
  - **kube-proxy:** Maintains network rules on nodes using `iptables` or `IPVS`, routing traffic internally to the correct Pods.
  - **Container Runtime:** The underlying software (containerd, CRI-O) physically running the containers.
- **Docker vs Kubernetes:** Docker physically builds and runs a single container image. Kubernetes orchestrates thousands of running containers across hundreds of virtual machines.
- **Docker Swarm vs Kubernetes:** Swarm is natively integrated with Docker—it's simpler but highly limited. Kubernetes is infinitely extensible (CRDs, Service Meshes, Operators), features complex RBAC, and is horizontally scalable to thousands of nodes.
- **Container vs Pod:** A container is an isolated Linux process. A **Pod** is Kubernetes' smallest deployable logical unit. A Pod can contain *multiple* tightly coupled containers sharing the same Network Namespace (IP address) and IPC namespace.
- **Namespace:** A logical partition inside a single physical K8s cluster. It acts as a virtual cluster, isolating RBAC permissions, Resource Quotas, and Network Policies between tenants (e.g., `dev` vs `prod`).
- **Services:** Abstract K8s objects that provide stable IP addresses and load balancing for dynamic Pods.
  - **ClusterIP:** Internal-only communication.
  - **NodePort:** Exposes the Service on a static port across *all* Worker Nodes.
  - **LoadBalancer:** Requests an external L4 Load Balancer from the underlying Cloud Provider (AWS ELB, Azure ALB).
- **Day-to-Day Activities:** SREs spend their days deploying YAML manifests (Helm, Kustomize), debugging CrashLoopBackOffs, monitoring Prometheus/Grafana alerts, rotating certificates, and writing RBAC policies.

## 💻 Essential Execution (Commands & YAML)

### 1. Generating a Pod (Declarative Setup)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: prod-web          # Isolating this exact pod
  labels:
    app: frontend
spec:
  containers:
  - name: nginx-container
    image: nginx:1.21.6
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```
```bash
# Imperatively generate a pod to test
kubectl run nginx-pod --image=nginx:1.21.6 --dry-run=client -o yaml > pod.yaml
```

### 2. Namespaces
```bash
# Create a namespace rapidly
kubectl create namespace prod-web

# Switch your local kubeconfig context permanently to this namespace
kubectl config set-context --current --namespace=prod-web
```

### 3. Exposing Traffic via NodePort vs LoadBalancer
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-nodeport
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - port: 80           # The ClusterIP port
      targetPort: 80     # The port ALREADY open on the actual Pod
      nodePort: 30007    # The explicit high port (30000-32767) opened on EVERY Worker Node
```
```bash
# Expose a deployment directly via an Azure/AWS external Load balancer
kubectl expose deployment frontend --type=LoadBalancer --port=80 --target-port=80
```

## ⚠️ Production Gotchas & Interview Traps
- **Trap (Docker vs K8s):** Candidates often say Kubernetes replaces Docker. **SRE Answer:** Kubernetes relies on a Container Runtime Interface (CRI) like containerd. Docker is an ecosystem for building images (OCI compliance); Kubernetes orchestrates them. (In fact, Kubernetes dropped dockershim entirely in v1.24).
- **Trap (Kubelet vs API Server):** If the API server goes down, do running pods die? **SRE Answer:** No! Existing pods keep running. The kubelet knows what it's running via its local cache. However, you cannot deploy new pods, scale up, or update states.
- **Trap (NodePort limits):** Using NodePort in production is poor practice because it bypasses centralized WAF and exposes massive ranges of node IPs. **SRE Answer:** Always use a LoadBalancer or an Ingress Controller backed by an internal Service in real-world enterprise infrastructure.
- **Gotcha (Namespaces):** Namespaces do NOT provide hard network isolation by default! A pod in `dev` can absolutely ping a pod in `prod` directly via its Pod IP unless you explicitly enforce `NetworkPolicies`.

## 🔍 Debugging (Where to look when it fails)
- `kubectl get events -n <namespace> --sort-by='.metadata.creationTimestamp'` (The absolute ultimate command to see *why* kubelet rejected a pod).
- `kubectl describe pod <pod-name>` (Critical for catching `ImagePullBackOff` or `OOMKilled` limits).
- `kubectl logs <pod-name> -c <container-name> -f` (Fetch application logs from standard output).
- `journalctl -u kubelet -f` (If a worker node goes `NotReady`, immediately SSH into the node and check the kubelet daemon logs).
- `kubectl exec -it <pod-name> -- /bin/sh` (Drop into the container network namespace for interactive DNS/curl testing).
- `kubectl get svc` (Check if your LoadBalancer is permanently stuck in `<pending>`, usually indicating a cloud-provider IAM role issue).

## 📝 10-Second Cheat Sheet
Kubernetes is a declarative orchestration engine for managing fleets of generic compute instances natively running containers. The Control Plane (API Server, ETCD, Scheduler, Controller Manager) acts as the brain dictating state, while Worker Nodes (kubelet, kube-proxy, container runtime) execute the raw muscle logic. A Pod is the smallest unit of execution grouping containers securely, while Namespaces logically fragment the cluster tenant space. Traffic is routed to Pods via Services, with NodePorts opening raw node access and LoadBalancers hooking directly into real-world Cloud Provider IPs. As an SRE, your day is dominated by debugging broken YAML state, tracking down OOM limits with `kubectl describe`, and securing multi-tenant APIs.
