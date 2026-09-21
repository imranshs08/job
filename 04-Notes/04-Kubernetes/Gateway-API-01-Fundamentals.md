# 🌩️ Session 1: Kubernetes Gateway API vs Ingress

> **Source:** Gateway API Sprint - Video 1 (Kubernetes Gateway API - Is Ingress dead?)
> **Domain:** Kubernetes Orchestration & Networking

---

## 🧠 The Why: Why is Ingress "Dead"?

For years, **Ingress** was the standard way to expose Kubernetes pods to the outside world (Domain with TLS → Azure Load Balancer → Ingress → Service → Pods). It provided a single entry point, better routing options than `LoadBalancer` types, and TLS termination via tools like `cert-manager`.

However, Ingress reached its limits in modern enterprise environments:
- **Vendor Lock-in (The "Annotation Soup"):** Ingress controllers (Traefik, NGINX, Azure AGIC) route traffic differently. Engineers rely on vendor-specific annotations (e.g., `nginx.ingress.kubernetes.io/use-regex: "true"`), making it impossible to migrate controllers without entirely rewriting manifests.
- **Strict Namespace Boundaries:** TLS secrets and Ingress rules *must* reside in the exact same namespace as the target pods. Secure cross-namespace routing is not natively supported.
- **Lack of Advanced Traffic Policy:** Native Ingress lacks complex capabilities like weighted load balancing, header-based routing, or protocol support beyond HTTP/HTTPS (e.g., TCP/UDP).

**The Solution:** The **Gateway API** — a modular, extensible, and role-oriented standard built directly into Kubernetes to solve these exact problems.

---

## 🏛️ Architecture: Gateway API Topology

Unlike the monolithic `Ingress` object, the Gateway API breaks routing down into modular components. This allows different roles (Platform/Infra teams vs. App Developers) to manage their respective configurations safely across different namespaces.

```mermaid
graph TD
    subgraph "Platform Team (Cluster Scope)"
        GC[GatewayClass<br>e.g., Azure AGC / Envoy] --> GW[Gateway<br>example.com]
    end
    
    subgraph "App Team (Namespace A)"
        GW -->|Listeners<br>(Port 80/443, TLS)| R1[HTTPRoute]
        R1 -->|Path: /api| S1[Service]
        S1 --> P1[Pods]
    end
    
    subgraph "Security Team (Namespace B)"
        TLS[(TLS Secret)] -.->|Cross-Namespace<br>ReferenceGrant| GW
    end
    
    style GC fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style GW fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#fff
    style R1 fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#fff
    style TLS fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#fff
```

### Core Components
1. **GatewayClass:** Defines which underlying proxy/infrastructure will fulfill the gateway (similar to `IngressClass`).
2. **Gateway:** Represents the physical/logical load balancer. It contains **Listeners** (monitoring specific ports and protocols like HTTP, HTTPS, TLS, TCP, UDP) and governs TLS certificates.
3. **HTTPRoute (or TCPRoute/UDPRoute):** Configured by application owners to define allowed paths, headers, backend services, and advanced traffic rules like **weighted load balancing** or **canary releases**.

---

## 💻 Execution: The Shift in YAML

### ❌ The Legacy Way (Ingress)
*Notice the heavy use of proprietary annotations and a single monolithic manifest locking the application to NGINX.*
```yaml
kind: Ingress
apiVersion: networking.k8s.io/v1
metadata:
  name: customerapi-prod
  namespace: customerapi-prod
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/use-regex: 'true' # ⚠️ Vendor Lock-in!
spec:
  tls:
    - hosts: [customer.programmingwithwolfgang.com]
      secretName: customerapi-tls # ⚠️ Must be in the exact same namespace
  rules:
    - host: customer.programmingwithwolfgang.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: customerapi, port: { number: 80 } }
```

### ✅ The Modern Way (Gateway API)
*Going forward in this sprint, we will split routing into a `Gateway` (managed by Infra) and an `HTTPRoute` (managed by Devs).* *(Examples to follow in upcoming labs)*.

---

## ⚠️ Production Gotchas & Interview Traps

*   **Interview Trap:** *"Why can't we just use Ingress for TCP traffic?"*
    *   **Answer:** Native Ingress is strictly designed for Layer 7 HTTP/HTTPS traffic. To route raw TCP/UDP, you usually have to hack the NGINX ConfigMap directly. Gateway API fixes this natively using `TCPRoute` and `UDPRoute`.
*   **Gotcha:** **Cross-Namespace Secrets.** In traditional Ingress, if you generate a wildcard cert via Cert-Manager in the `security` namespace, you cannot natively use it in the `frontend` namespace. Gateway API introduces **`ReferenceGrant`**, explicitly allowing a Gateway in Namespace A to safely consume a TLS Secret in Namespace B.
*   **Advanced Capabilities:** Native mTLS configuration, weighted load balancing (traffic splitting), and header manipulation are built directly into the Gateway API route specifications without requiring vendor-specific annotation hacks.
