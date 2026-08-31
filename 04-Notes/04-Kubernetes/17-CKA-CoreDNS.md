# CKA Cheat Sheet: CoreDNS & Manual Networking

> **Scope**: Services & Networking (20%)  
> **Tracker Link**: [README.md](README.md)

Understanding how names resolve inside the cluster is critical for debugging connectivity issues between microservices.

---

## 1. CoreDNS Fundamentals

CoreDNS runs as a Deployment in the `kube-system` namespace. It watches the Kubernetes API for new Services and Endpoints and creates DNS records for them dynamically.

- **Pod Name:** `coredns-*`
- **ConfigMap:** `coredns` (inside `kube-system` namespace). This contains the `Corefile` where DNS forwarding rules exist.

### 💡 The FQDN (Fully Qualified Domain Name) Format
`[service-name].[namespace].svc.cluster.local`

If you are inside a pod in the `payment` namespace and you want to curl a service named `db` in the `backend` namespace, you MUST use:
`curl db.backend.svc.cluster.local`

*(If both pods were in the same namespace, `curl db` would be enough).*

---

## 2. Debugging DNS within a Pod

You will often need to spin up a temporary pod just to test DNS lookups across the cluster.

```bash
# Spin up a temporary busybox pod to run nslookup
kubectl run test-dns --image=busybox:1.28 --rm -it -- restart

# Once inside the shell, test the Service DNS
nslookup web-service.default.svc.cluster.local
```
*Why `busybox:1.28`? Newer versions of busybox have a known bug with `nslookup` in Kubernetes environments. Use 1.28 for the exam.*

### Checking the Pod's DNS config (`resolv.conf`)
If DNS is failing, check where the pod is pointing its queries:
```bash
cat /etc/resolv.conf
# It should point to the IP address of the kube-dns Service (e.g. nameserver 10.96.0.10)
```

---

## 3. Host Networking

Sometimes you need a Pod to bypass the Kubernetes overlay network entirely and connect directly to the underlying Node's network interface (acting as if it was a native linux process).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: host-network-pod
spec:
  hostNetwork: true       # <----- The critical line
  containers:
  - name: my-app
    image: nginx
```
*Warning: If this pod runs NGINX on port 80, no other `hostNetwork` pod can run on port 80 on that specific node, because the port is now physically bound on the host OS.*
