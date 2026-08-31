# CKA Cheat Sheet: Kubernetes Services

> **Scope**: Core Concepts (Networking)  
> **Tracker Date**: Aug 28 - Aug 30, 2026

Services in Kubernetes provide stable network endpoints to access dynamic, ephemeral Pods. They act as internal load balancers and route traffic based on label selectors.

---

## 1. Service Types

1. **ClusterIP (Default):** Exposes the Service on a cluster-internal IP. Accessible *only* from within the cluster.
2. **NodePort:** Exposes the Service on each Node's IP at a static port (default range: 30000-32767). Automatically creates a ClusterIP.
3. **LoadBalancer:** Provisions a cloud provider's external load balancer (e.g., AWS ALB/NLB) and automatically creates both a NodePort and ClusterIP.
4. **ExternalName:** Maps the Service to a DNS name (e.g., `db.example.com`), allowing pods to bypass cluster DNS.

---

## 2. ⚡ Imperative Commands (CKA Speed Strategy)

Creating services imperatively is crucial for the CKA exam to save time writing YAML.

```bash
# Create a ClusterIP targeting port 80 on pods
kubectl expose pod redis --port=6379 --name redis-service

# Create a NodePort service targeting a deployment
kubectl expose deployment frontend --name=frontend-svc --type=NodePort --port=80 --target-port=8080

# Dry-run to generate YAML
kubectl expose pod nginx --port=80 --dry-run=client -o yaml > svc.yaml

# Explicitly create a service without exposing an existing resource
kubectl create service clusterip my-svc --tcp=5678:8080
kubectl create service nodeport my-ns-svc --tcp=80:80
```

---

## 3. Endpoints (The Hidden Engine)

A Service does not route traffic directly to Pods. It routes traffic to **Endpoints**.
When you create a Service with a `selector`, Kubernetes automatically creates an `Endpoints` object with the same name.

- **Check Endpoints:** `kubectl get endpoints <service-name>`
- **No Selector?** You must create the Endpoints object manually.

### 💡 CKA Troubleshooting Tip:
If a Service is not working, check the endpoints first!
`kubectl describe svc my-service` -> Look for the `Endpoints:` field. If it says `<none>`, your selector does not match the labels on your pods!

---

## 4. DNS Resolution in K8s

Internal services resolve via CoreDNS. The standard FQDN format is:
`service-name.namespace.svc.cluster.local`

- From the *same namespace*: Just curl `http://service-name`
- From a *different namespace*: curl `http://service-name.other-namespace`

---

## 5. Typical Interview Question

**Q: How does a NodePort service route traffic under the hood?**
*A: When a request hits NodePort on any node, `kube-proxy` (usually running iptables or IPVS modes) intercepts the packet. It performs Destination NAT (DNAT), translating the Request IP to a specific Pod's IP (via the Endpoints tracking list), and forwards it across the overlay network (e.g., Flannel, Calico).*
