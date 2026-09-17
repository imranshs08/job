# 📘 DAY-37 | KUBERNETES SERVICES DEEP DIVE| LIVE DEMO | LEARN TRAFFIC FLOW USING KUBESHARK |

## 🎯 The "Why" (Core Concept)
- **Kubeshark** is an API traffic analyzer for Kubernetes, essentially acting as a **Wireshark for your K8s clusters**. It provides deep visibility into pod-to-pod communication without requiring sidecar proxies or code changes.
- *Analogy:* Imagine trying to track down a lost package in a massive automated warehouse where drones are constantly flying around. **Kubeshark** is like suddenly giving you a god-level X-ray view of the entire facility, showing you exactly which drone dropped the package, when, and to whom.
- **Catastrophic Problem Solved:** It instantly solves the "ghost in the machine" microservice debugging nightmare where requests are sporadically timing out or dropping, and traditional application logs offer completely blind visibility into the actual network packets traversing the cluster's CNI (Container Network Interface).

## ⚙️ Architecture & Under the Hood
- **eBPF (Extended Berkeley Packet Filter):** Kubeshark leverages the power of eBPF at the kernel level to capture API traffic at scale with near-zero overhead.
- **Worker DaemonSet:** When deployed, it spins up a highly privileged DaemonSet on your worker nodes to intercept raw packet data traversing the node's virtual ethernet (`veth`) network interfaces.
- **Hub & CLI Architecture:** The CLI (`kubeshark.exe`) communicates with a central Hub deployment situated in the cluster, which aggregates and streams the tapped traffic back to your terminal or a web-based UI.
- **No Sidecar Requirement:** Unlike service meshes (Istio, Linkerd), it does not inject `Envoy` proxies, meaning it can be dynamically injected into a cluster during an incident without mutating running deployments.
- **Protocol Decoding:** It automatically decodes REST, gRPC, Kafka, Redis, and AMQP payloads locally on the node before transferring them, preserving bandwidth.

## 💻 Essential Execution (Commands & YAML)

**1. Minikube Installation (Windows - PowerShell as Admin)**
```powershell
# Using Winget (Preferred Windows Package Manager) to fetch the latest Minikube binary
winget install minikube

# Start Minikube with sufficient resources for packet capture & container builds
minikube start --memory=4096 --cpus=2

# Verify cluster control-plane and kubelet status
minikube status
```

**2. Kubeshark Installation & Execution (Windows - PowerShell)**
```powershell
# Download the Kubeshark binary for Windows
curl.exe -LO "https://github.com/kubeshark/kubeshark/releases/latest/download/kubeshark.exe"

# Move the executable to a directory in your PATH (e.g., C:\Windows\System32 or create an alias)
Move-Item -Path ".\kubeshark.exe" -Destination "C:\Windows\System32\kubeshark.exe" -Force

# Start capturing ALL traffic in the default namespace
kubeshark.exe tap

# Start capturing traffic specifically for a deployment (e.g., python-api)
kubeshark.exe tap "pod.name == 'python-api'"
```

**3. Application Simulation: Python Dockerfile & Build (PowerShell)**
```dockerfile
# Dockerfile: Basic Python API for traffic testing
FROM python:3.9-slim
WORKDIR /app
# Quick inline HTTP server to simulate an endpoint on port 8080
CMD ["python", "-m", "http.server", "8080"]
```
```powershell
# Point your host's Docker CLI to the internal Minikube Docker daemon
minikube docker-env | Invoke-Expression

# Build the Docker image locally within minikube to avoid needing an external image registry
docker build -t python-api:v1 . 
```

**4. Kubernetes Deployment YAML for Simulation**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-api-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: python-api
  template:
    metadata:
      labels:
        app: python-api
    spec:
      containers:
      - name: api-container
        image: python-api:v1
        imagePullPolicy: Never # CRITICAL: Forces Kubernetes to use the local minikube-built image
        ports:
        - containerPort: 8080
```
```powershell
# Declaratively apply the deployment to the cluster
kubectl apply -f deployment.yaml
```

**5. Advanced Kubectl Verbosity & Troubleshooting**
```powershell
# Get pods with extended verbosity level 7 (Shows HTTP requests made by the kubectl client itself)
kubectl get po -v=7

# Maximum verbosity (Level 9) - dumps raw curl API payloads, tokens, and headers for deep API server debugging
kubectl get po -v=9
```

**6. Node-Level Connectivity Testing**
```powershell
# SSH directly into the minikube control-plane/worker node bypassing the K8s API
minikube ssh

# Perform a raw curl test directly against the Pod's internal IP and Port from the host network
# (Replace 10.244.0.X with the actual Pod IP found via 'kubectl get po -o wide')
curl -v http://10.244.0.X:8080
```

## ⚠️ Production Gotchas & Interview Traps
- **Production Gotcha - EBPF Kernel Panics/Compatibility:** Kubeshark relies heavily on eBPF. If you deploy this onto an older, legacy Kubernetes cluster running archaic Linux kernels (pre-4.15), it will fail to attach the probes and can potentially destabilize node networking.
- **Production Gotcha - Disk/Memory Exhaustion:** Leaving a root-level packet capture running indefinitely on a high-throughput production cluster (e.g., thousands of RPS) will rapidly exhaust memory or disk IOPS on the worker nodes collecting the PCAP data. Keep sessions short.
- **SRE Interview Trap:** "How do you trace a dropped HTTP packet between two Microservices?" 
  - *Bad Answer:* "I'll look at the application logs or install a Service Mesh to get tracing." 
  - *SRE Answer:* "If a Service Mesh isn't already present, I won't introduce architectural drift or restart pods during an active outage. I will deploy an ephemeral eBPF-based sniffer like **Kubeshark** or inject an ephemeral debug container with `tcpdump` to capture raw ring-buffer traffic on the host's `veth` interfaces securely, without disrupting the running workloads."

## 🔍 Debugging (Where to look when it fails)
- **`kubectl get pods -n kubeshark`** - Verify the Hub and Worker DaemonSets actually transitioned to the `Running` state without `CrashLoopBackOff`.
- **`kubectl logs -l app=kubeshark-worker -n kubeshark`** - Check the worker logs to see if eBPF probes are failing to attach due to kernel permission restrictions or AppArmor profiles blocking access.
- **`kubeshark.exe check`** - Run the built-in pre-flight diagnostic CLI tool to validate cluster kernel compatibility and RBAC permissions.
- **`minikube logs`** - Check the underlying hypervisor or container logs if Minikube networking collapses entirely.
- **`cat /sys/kernel/debug/tracing/trace_pipe`** (run inside the node) - Deep kernel inspection to monitor if eBPF hooks are logging systemic trace errors on the host node.

## 📝 10-Second Cheat Sheet
**Kubeshark** is an ephemeral, eBPF-powered packet analyzer for Kubernetes that gives you immediate WireShark-level visibility into pod-to-pod traffic without altering your Deployments or requiring a heavyweight Service Mesh. It deploys as a privileged DaemonSet to tap kernel-level network interfaces, decoding REST/gRPC traffic on the fly. When debugging network timeouts or `Connection Refused` errors, avoid injecting permanent sidecars during an incident; instead, use `kubeshark tap` to rapidly isolate the failing network hops. Use `kubectl get po -v=9` to heavily debug the Kubernetes API server client calls, and execute `minikube ssh` coupled with a manual `curl` for brute-force, low-level node connectivity tests.
