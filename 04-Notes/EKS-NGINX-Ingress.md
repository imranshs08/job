# EKS NGINX Ingress Controller Configuration

This guide demonstrates a production-grade NGINX Ingress configuration for an AWS EKS cluster, featuring TLS termination, path-based routing, and rate limiting (throttling) to protect your microservices.

## 1. Prerequisites
- **NGINX Ingress Controller** installed via Helm.
- **cert-manager** installed (optional, but recommended for auto-TLS).
- A domain name (e.g., `api.example.com`) pointing to the Classic/Network Load Balancer created by the NGINX Ingress service.

---

## 2. The Ingress Configuration (`ingress.yaml`)

This manifest routes traffic to two distinct microservices (`users-service` and `orders-service`) using path-based rules. It also enforces a rate limit to prevent abuse.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: microservices-ingress
  namespace: prod
  annotations:
    # 1. Specify the NGINX Ingress Class
    kubernetes.io/ingress.class: "nginx"

    # 2. TLS / SSL Settings
    # If using cert-manager, this will automatically issue a Let's Encrypt cert
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    # Force redirect HTTP to HTTPS
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # 3. Path rewriting (strips the prefix before sending to the pod)
    # E.g., /api/v1/users/123 -> /123 (if backend expects root path)
    nginx.ingress.kubernetes.io/rewrite-target: /$2

    # 4. Rate Limiting Rules (Throttling)
    # Limit requests from a single IP to 10 requests per second
    nginx.ingress.kubernetes.io/limit-rps: "10"
    # Allow a burst of 5 additional requests before rejecting with 503
    nginx.ingress.kubernetes.io/limit-burst-multiplier: "5"
    # Wait time (in connections/seconds) before rejecting further requests
    nginx.ingress.kubernetes.io/limit-connections: "20"
spec:
  # TLS Termination Definition
  tls:
    - hosts:
        - api.example.com
      # The Secret where the TLS certificate is stored (managed by cert-manager)
      secretName: api-example-tls-secret
  
  # Path-Based Routing Rules
  rules:
    - host: api.example.com
      http:
        paths:
          # Microservice 1: Users Service
          - path: /api/v1/users(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: users-service
                port: 
                  number: 8080
          
          # Microservice 2: Orders Service
          - path: /api/v1/orders(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: orders-service
                port: 
                  number: 8080
```

---

## 3. Configuration Breakdown

### 🔐 TLS Termination
- `nginx.ingress.kubernetes.io/ssl-redirect: "true"`: Automatically redirects any port 80 (HTTP) traffic to port 443 (HTTPS).
- `tls.secretName`: NGINX uses the certificate stored in this Kubernetes `Secret` to terminate the TLS session before forwarding plain HTTP traffic to your microservices in the cluster.

### 🚦 Rate Limiting
- `limit-rps: "10"`: This is a preventative security measure. It restricts any single client IP address to 10 requests per second.
- `limit-burst-multiplier: "5"`: Allows short bursts of traffic (up to 50 requests rapidly) to accommodate real-world UI loading mechanics before dropping packets. 
- *Pro-Tip:* When a client hits the rate limit, NGINX returns an `HTTP 503 Service Unavailable` (or optionally `429 Too Many Requests` via custom errors).

### 🔀 Path-Based Routing (Regex & Rewrite)
- `path: /api/v1/users(/|$)(.*)`: Matches anything starting with `/api/v1/users`. 
- `rewrite-target: /$2`: When traffic hits the `users-service`, the `/api/v1/users` prefix is stripped off. For example, a request to `api.example.com/api/v1/users/login` hits the pod as `/login`.

---
*Generated for interview preparation & EKS deployment checklists.*
