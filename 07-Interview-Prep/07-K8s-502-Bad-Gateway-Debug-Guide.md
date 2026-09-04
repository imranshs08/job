# 🔥 Production-Grade Kubernetes Networking Debugging Guide

> **Template Prompt:**
> *"My Kubernetes cluster has the following issue: [describe]. Cluster: [EKS/AKS/Kind]. Version: [version]. Error: [paste error]. Provide a step-by-step debugging approach with kubectl commands."*

---

## 🎯 Scenario: 502 Bad Gateway / Ingress Failing

- **Cluster:** Azure AKS / AWS EKS
- **Ingress Controller:** Nginx
- **Symptom:** Users visiting `https://api.mycompany.com` are receiving a `502 Bad Gateway` error instead of the application response.

---

## 📋 Phase 1: Triage — Where is the failure?

A 502 error in Kubernetes means the Ingress Controller received the request, but it cannot reach the backend Service or Pods. The chain is: **Browser ➡️ Ingress ➡️ Service ➡️ Pods**.

### Step 1.1 — Check the Ingress Object

```bash
kubectl get ingress api-ingress -n production
```

**Actual Output:**
```
NAME          CLASS    HOSTS                 ADDRESS        PORTS     AGE
api-ingress   nginx    api.mycompany.com     20.55.10.100   80, 443   145d
```

### Step 1.2 — Confirm the Service Mapping

```bash
kubectl describe ingress api-ingress -n production
```

**Actual Output (key section):**
```
Rules:
  Host               Path  Backends
  ----               ----  --------
  api.mycompany.com  /     payment-service:8080 (10.244.1.15:8080,10.244.2.33:8080)
```
> 🟡 **Note:** The Ingress thinks it should route to `payment-service` on port `8080`. It sees 2 Pod IPs (`10.244...`).

---

## 📋 Phase 2: Deep Dive — Inspect the Service & Endpoints

### Step 2.1 — Does the Service match the Pods?

```bash
# Describe the service to check its selectors and TargetPort
kubectl describe svc payment-service -n production
```

**Actual Output:**
```
Name:              payment-service
Namespace:         production
Selector:          app=payment-api,tier=backend
Type:              ClusterIP
IP:                10.0.15.200
Port:              http  8080/TCP
TargetPort:        80/TCP                   ← ⚠️ MISMATCH
Endpoints:         10.244.1.15:80,10.244.2.33:80
```

> 🔴 **Red Flag #1 (TargetPort Mismatch):** The Ingress is routing to port `8080`, but the Service is forwarding traffic to port `80` on the Pods. If the NodeJS/Java Pods are actually listening on `8080`, all connections will fail.

### Step 2.2 — Test connectivity directly from inside the cluster

Let's exec into a temporary debug pod and try to curl the service directly. This proves if the Service is working or broken.

```bash
kubectl run -i --tty --rm debug --image=curlimages/curl --restart=Never -n production -- sh
```

Inside the debug pod:
```bash
# Try hitting the service
curl -v http://payment-service:8080
```

**Actual Output:**
```
*   Trying 10.0.15.200:8080...
* connect to 10.0.15.200 port 8080 failed: Connection refused
* Failed to connect to payment-service port 8080: Connection refused
```

---

## 📋 Phase 3: Inspect the Pods Directly

Let's see what the backend pods are actually doing.

### Step 3.1 — Check Pod Status

```bash
kubectl get pods -l app=payment-api,tier=backend -n production -o wide
```

**Actual Output:**
```
NAME                           READY   STATUS    RESTARTS   AGE    IP            NODE
payment-api-6d9f4b7c8-4xkpz    1/1     Running   0          5m     10.244.1.15   aks-pool-1
payment-api-6d9f4b7c8-9wlmn    1/1     Running   0          5m     10.244.2.33   aks-pool-2
```
> The pods are Running and Ready. So why the 502?

### Step 3.2 — Check Pod Logs for App Errors

```bash
kubectl logs -l app=payment-api,tier=backend -n production --tail 20
```

**Actual Output:**
```
[INFO] Server starting...
[INFO] Loading environment variables
[INFO] Server listening on port 8080      ← 🎯 ROOT CAUSE REVEALED
```

---

## 📋 Phase 4: Resolution

### Root Cause Summary
- **App/Pod:** Listening on Port `8080`.
- **Service:** Mapping Port `8080` (ClusterIP) ➡️ TargetPort `80` (Pod).
- **Ingress:** Routing to Service on Port `8080`.

Because the Service was forwarding traffic to Pod port `80` (where nothing is listening), the kernel immediately rejects the connection. The Nginx Ingress receives `Connection refused`, resulting in a `502 Bad Gateway` being sent back to the user.

### Step 4.1 — Fix the Service Manifest

```bash
kubectl edit svc payment-service -n production
```

Change in editor:
```yaml
# BEFORE
ports:
  - port: 8080
    targetPort: 80

# AFTER
ports:
  - port: 8080
    targetPort: 8080
```

### Step 4.2 — Verify the Fix from the Debug Pod

```bash
curl -v http://payment-service:8080
```
**Output:** `HTTP/1.1 200 OK`

### Step 4.3 — Verify via Ingress (Browser Simulation)

```bash
# Check if the public route is working now
curl -v https://api.mycompany.com/health
```
**Output:** `HTTP/2 200`

---

## 🧠 Debug Decision Tree (K8s Networking Connectivity)

```
Ingress URL yields an Error
├── Error: 404 Not Found
│   ├── Check Ingress Host mapping (`kubectl get ingress`)
│   │   └── Ensure the request hostname matches the `Host:` block exactly.
│   └── Check Ingress Path (`/v1/api` vs `/`)
│       └── Use rewrite-target annotations if stripping the path is required.
│
├── Error: 502 Bad Gateway
│   ├── Ingress cannot reach backend Service/Pod.
│   ├── Check Service `Endpoints` (`kubectl get ep <svc-name>`).
│   │   ├── Endpoints = <none> → Pod Labels do not match Service Selectors!
│   │   └── Endpoints exist → TargetPort is wrong, NetworkPolicy is blocking it, or Pod is hanging.
│   │
│   └── Check Network Policies (`kubectl get netpol`)
│       └── Ensure Ingress controller namespace is whitelisted to access target namespace.
│
└── Error: 503 Service Unavailable / 504 Gateway Timeout
    ├── Ingress reached the Pod, but Pod took too long to answer.
    ├── High CPU/Load on Pod?
    └── Upstream DB is slow/locked? (Check application logs).
```
