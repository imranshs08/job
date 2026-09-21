# 🌐 Lab: Cloudflare Tunnel (trycloudflare.com)
# Expose Local Services to the Internet — Zero Config, No Account

> **Lab Directory:** `11-Labs-and-Validation/`
> **Difficulty:** ⭐⭐ Intermediate
> **Time:** ~45–60 minutes
> **Prerequisites:** Docker Desktop, Minikube (optional), Python 3, curl

---

## 🎯 The "Why" — DevOps Analogy

> Think of Cloudflare Tunnel like a **reverse SSH tunnel on steroids** — but with TLS, DDoS protection, and zero firewall rules. Instead of punching a hole in your router, Cloudflare's global edge network carries the traffic FROM the internet TO your local machine through an outbound-only encrypted connection. **No inbound ports. No public IPs. No NAT rules.**

### Real-World DevOps Use Cases This Lab Covers

| Scenario | Why It Matters |
|----------|---------------|
| Expose a local API for Webhook testing (GitHub, Stripe) | No need for ngrok or VPN |
| Share a Minikube/Kind service with a remote reviewer | Instant external URL for K8s NodePort |
| Test a Dockerized app before pushing to staging | Full prod-like HTTPS URL |
| Cloudflare as a zero-trust perimeter for home labs | Foundation for enterprise Zero-Trust |
| Load test your local service from an external tool | Real external traffic simulation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Your Local Machine                      │
│                                                         │
│   ┌─────────────┐    ┌──────────────┐                  │
│   │  Local App  │◄──►│  cloudflared │──── outbound ───►│
│   │ :8080       │    │  (daemon)    │                  |
│   └─────────────┘    └──────────────┘                  │
└─────────────────────────────────────────────────────────┘
                                │
                    Encrypted Tunnel (QUIC/H2)
                                │
                ┌───────────────▼───────────────┐
                │   Cloudflare Edge Network      │
                │   (200+ PoPs globally)         │
                └───────────────┬───────────────┘
                                │
                    https://random-name.trycloudflare.com
                                │
                        ┌───────▼────────┐
                        │  End User /    │
                        │  GitHub Webhook│
                        │  / Reviewer    │
                        └────────────────┘
```

**Key insight for the exam / interviews:**
- `cloudflared` makes an **outbound connection only** → no firewall rules needed
- Traffic flows: Internet → Cloudflare Edge → Tunnel → Your localhost
- TLS is terminated at Cloudflare Edge (HTTPS for free, no cert management)

---

## 🛠️ Part 1 — Install `cloudflared`

### Option A: Windows (Winget) — Recommended
```powershell
# Install via Windows Package Manager
winget install Cloudflare.cloudflared

# Verify installation
cloudflared --version
```

### Option B: Windows (Direct Binary)
```powershell
# Download latest release
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" `
  -OutFile "C:\Windows\System32\cloudflared.exe"

# Verify
cloudflared --version
```

### Option C: Linux (Ubuntu/Debian) — for WSL2 or VM
```bash
# Add Cloudflare package repo
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-main.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list

sudo apt update && sudo apt install -y cloudflared

# Verify
cloudflared --version
```

### Option D: Docker (No Install Required!) ✅
```bash
# Run entirely in a container — no local binary needed
docker pull cloudflare/cloudflared:latest
cloudflared --version  # aliased below in lab
```

---

## 🧪 Part 2 — Use Case 1: Expose a Python API

### Step 1: Create a simple Python Flask API
```bash
# Create lab directory
mkdir -p C:\Job Tracker\11-Labs-and-Validation\cloudflare-tunnel-lab
cd "C:\Job Tracker\11-Labs-and-Validation\cloudflare-tunnel-lab"
```

```python
# app.py — Save this file in the lab directory
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        payload = {
            "status": "healthy",
            "service": "CloudflareTunnelLab",
            "path": self.path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "headers": {
                # Cloudflare adds these headers — useful for identity verification
                "CF-Connecting-IP": self.headers.get("CF-Connecting-IP", "not-set"),
                "CF-Ray": self.headers.get("CF-Ray", "not-set"),
                "CF-Visitor": self.headers.get("CF-Visitor", "not-set"),
            }
        }
        self.wfile.write(json.dumps(payload, indent=2).encode())

    def log_message(self, format, *args):
        print(f"[{datetime.utcnow().isoformat()}] {format % args}")

if __name__ == "__main__":
    port = 8080
    print(f"🚀 Server listening on http://localhost:{port}")
    HTTPServer(("", port), Handler).serve_forever()
```

### Step 2: Start the local server
```bash
# Terminal 1 — Run the API
python app.py
# Expected output: 🚀 Server listening on http://localhost:8080
```

### Step 3: Verify it works locally first
```bash
# Terminal 2 — Test local
curl http://localhost:8080/health
```

Expected output:
```json
{
  "status": "healthy",
  "service": "CloudflareTunnelLab",
  "path": "/health",
  "timestamp": "2026-09-21T00:00:00Z",
  "headers": {
    "CF-Connecting-IP": "not-set",
    "CF-Ray": "not-set",
    "CF-Visitor": "not-set"
  }
}
```

### Step 4: Launch the Cloudflare Tunnel
```bash
# Terminal 2 — Start the tunnel
cloudflared tunnel --url http://localhost:8080

# ✅ Expected output (after ~5 seconds):
# +--------------------------------------------------------------------------------------------+
# |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
# |  https://random-words-here.trycloudflare.com                                               |
# +--------------------------------------------------------------------------------------------+
```

> ⚠️ **Production Gotcha:** The URL changes EVERY time you restart `cloudflared`. For persistent URLs, you need a free Cloudflare account and a named tunnel. `trycloudflare.com` = ephemeral/dev only.

### Step 5: Test from the internet
```bash
# Replace with YOUR generated URL
export TUNNEL_URL="https://your-random-url.trycloudflare.com"

# Test 1: Health check
curl $TUNNEL_URL/health

# Test 2: Check Cloudflare headers — this is the KEY learning
curl -s $TUNNEL_URL/health | python -m json.tool

# You should now see CF-Connecting-IP and CF-Ray populated!
# CF-Ray = Cloudflare's unique request trace ID (like a distributed trace)
# CF-Connecting-IP = the REAL IP of whoever called your API
```

### 🔬 Observation Checkpoint
| What to observe | Why it matters |
|----------------|---------------|
| `CF-Connecting-IP` shows real IP | Cloudflare strips original IP but passes it in this header |
| `CF-Ray` is populated | This is a global trace ID — used in Cloudflare logs |
| HTTP → HTTPS upgrade | Cloudflare terminates TLS — your code stays plain HTTP |
| Response time from phone/4G | Measures Cloudflare edge PoP latency vs. direct |

---

## 🐳 Part 3 — Use Case 2: Expose a Docker Container

### Step 1: Run a service in Docker
```bash
# Run a standard Nginx container
docker run -d --name cf-lab-nginx -p 8081:80 nginx:alpine

# Verify it's running
curl http://localhost:8081
```

### Step 2: Tunnel it with cloudflared (Docker way — no install needed)
```bash
# Run cloudflared as a Docker container pointing to host's port 8081
docker run --rm --network host \
  cloudflare/cloudflared:latest \
  tunnel --url http://localhost:8081

# On Windows (Docker Desktop), use host.docker.internal instead:
docker run --rm \
  cloudflare/cloudflared:latest \
  tunnel --url http://host.docker.internal:8081
```

### Step 3: Test from your phone browser
```bash
# Copy the generated HTTPS URL and open it on your mobile device
# You should see the Nginx "Welcome to nginx!" page over HTTPS
```

### Cleanup
```bash
docker stop cf-lab-nginx && docker rm cf-lab-nginx
```

---

## ☸️ Part 4 — Use Case 3: Expose a Kubernetes Service (Minikube)

> **DevOps Interview Gold:** *"How would you share a Kubernetes NodePort service with a remote stakeholder without exposing your cluster publicly?"*

### Step 1: Start Minikube and deploy a test app
```bash
# Start Minikube (if not already running)
minikube start --driver=docker

# Deploy a test app
kubectl create deployment cf-demo --image=nginx:alpine
kubectl expose deployment cf-demo --port=80 --type=NodePort

# Get the NodePort URL
minikube service cf-demo --url
# Example output: http://127.0.0.1:53241
```

### Step 2: Tunnel the NodePort via cloudflared
```bash
# Use the URL from minikube service output above
cloudflared tunnel --url http://127.0.0.1:53241

# Now anyone with the trycloudflare.com URL can see your K8s-served page
```

### Step 3: Or use kubectl port-forward + tunnel
```bash
# Terminal 1 — Port forward the service
kubectl port-forward svc/cf-demo 9090:80

# Terminal 2 — Tunnel the forwarded port
cloudflared tunnel --url http://localhost:9090
```

> 📝 **Key architectural distinction:**
> - `minikube service --url` = uses the NodePort (external K8s traffic path)
> - `kubectl port-forward` = bypasses Service, goes direct to pod (debugging path)
> - For demos: port-forward is cleaner and works on any cluster (EKS, AKS, Kind)

### Cleanup
```bash
kubectl delete deployment cf-demo
kubectl delete service cf-demo
```

---

## 🔔 Part 5 — Use Case 4: Webhook Receiver (GitHub → Local)

> This is the #1 real-world DevOps use for ephemeral tunnels — testing GitHub webhooks, Stripe events, or Slack slash commands locally **without deploying**.

### Step 1: Create a Webhook receiver
```python
# webhook_receiver.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        print("\n" + "="*60)
        print(f"📥 WEBHOOK RECEIVED: {self.path}")
        print(f"📋 Event: {self.headers.get('X-GitHub-Event', 'unknown')}")
        print(f"🔑 Delivery: {self.headers.get('X-GitHub-Delivery', 'unknown')}")
        print("📦 Payload:")
        try:
            print(json.dumps(json.loads(body), indent=2)[:1000])  # truncate large payloads
        except Exception:
            print(body[:500].decode(errors='replace'))
        print("="*60 + "\n")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"received": true}')

    def log_message(self, *args): pass  # quiet HTTP logs

HTTPServer(("", 7070), WebhookHandler).serve_forever()
```

### Step 2: Start receiver + tunnel
```bash
# Terminal 1
python webhook_receiver.py

# Terminal 2
cloudflared tunnel --url http://localhost:7070
# Copy the generated URL, e.g. https://abc-def-ghi.trycloudflare.com
```

### Step 3: Register as a GitHub Webhook
1. Go to your GitHub repo → **Settings → Webhooks → Add webhook**
2. **Payload URL:** `https://abc-def-ghi.trycloudflare.com/github`
3. **Content type:** `application/json`
4. **Events:** Select "Push events" or "All events"
5. Click **Add webhook** → GitHub sends a ping event immediately
6. Watch your Terminal 1 — you'll see the live JSON payload!

### Step 4: Trigger an event
```bash
# Make a commit and push to your repo
git commit --allow-empty -m "test webhook"
git push

# Watch Terminal 1 for the push event payload
```

---

## 🔬 Part 6 — Production Gotchas & Interview Traps

### ⚠️ Gotcha 1: Ephemeral URLs = Dev Only
- `trycloudflare.com` gives a **new random URL every restart** — cannot be used for permanent webhooks in production
- **Production fix:** Use `cloudflared tunnel create <name>` with a Cloudflare account + persistent DNS CNAME

### ⚠️ Gotcha 2: No Authentication by Default
- Anyone with the URL can access your service — it's **fully public**
- **Production fix:** Add `--access-policy` or enable Cloudflare Access (Zero Trust) in front of the tunnel

### ⚠️ Gotcha 3: Cloudflare Rewrites Headers
- `Host` header is rewritten to `*.trycloudflare.com` — apps that validate `Host` header will fail
- **Fix:** Pass `--http-host-header localhost:8080` to preserve original host

### ⚠️ Gotcha 4: WebSocket Support
- WebSockets work but require `--proxy-keepalive-connections` flag for stability
- gRPC requires HTTP/2 explicitly: `cloudflared tunnel --url grpc://localhost:50051 --http2-origin`

### ⚠️ Gotcha 5: TLS Between cloudflared → Origin
- By default, cloudflared connects to your origin over HTTP (plain)
- If your local app has a self-signed cert: `cloudflared tunnel --url https://localhost:8443 --no-tls-verify`

---

## 🎤 Interview Q&A — Senior DevOps Level

**Q: What is the fundamental difference between Cloudflare Tunnel and a traditional reverse proxy like Nginx?**
> **SRE Answer:** A traditional reverse proxy (Nginx/HAProxy) requires **inbound port exposure** — you must open firewall ports and have a public IP. Cloudflare Tunnel uses **outbound-only QUIC/TCP connections** from the `cloudflared` daemon to Cloudflare's edge. No inbound ports, no public IP, no NAT configuration — Cloudflare's edge forwards traffic back through the established outbound connection. This is the foundation of Zero-Trust networking.

**Q: How would you use Cloudflare Tunnel to implement Zero-Trust access for an internal admin dashboard?**
> **SRE Answer:** Deploy the `cloudflared` daemon as a Kubernetes DaemonSet or Deployment alongside the admin service. Create a named tunnel pointing at the internal ClusterIP service. Enable **Cloudflare Access** in front of the tunnel, which enforces IdP authentication (Azure AD/Okta) before any traffic reaches the origin. Users authenticate at Cloudflare's edge — the internal service never sees unauthenticated traffic. Zero VPN, zero inbound firewall rules.

**Q: How is trycloudflare.com different from a production named tunnel?**
> **SRE Answer:** `trycloudflare.com` is a free, no-account ephemeral service — the URL is randomly generated and changes every restart. Production named tunnels use `cloudflared tunnel create <name>`, persist their config in `~/.cloudflared/`, and expose a stable CNAME DNS record. Named tunnels support routing rules, load balancing across multiple replicas, and Cloudflare Access policies.

---

## ⚡ Quick Reference Card

```bash
# ── INSTALL ──────────────────────────────────────────────
winget install Cloudflare.cloudflared              # Windows
brew install cloudflare/cloudflare/cloudflared     # macOS
apt install cloudflared                            # Linux

# ── EXPOSE LOCAL PORT ────────────────────────────────────
cloudflared tunnel --url http://localhost:8080

# ── DOCKER RUN (no install) ──────────────────────────────
docker run --rm cloudflare/cloudflared tunnel --url http://host.docker.internal:8080

# ── WITH HOSTNAME HEADER FIX ─────────────────────────────
cloudflared tunnel --url http://localhost:8080 --http-host-header localhost:8080

# ── SELF-SIGNED CERT ORIGIN ──────────────────────────────
cloudflared tunnel --url https://localhost:8443 --no-tls-verify

# ── gRPC ORIGIN ──────────────────────────────────────────
cloudflared tunnel --url grpc://localhost:50051 --http2-origin

# ── METRICS (built-in Prometheus endpoint) ───────────────
cloudflared tunnel --url http://localhost:8080 --metrics localhost:2999
curl http://localhost:2999/metrics
```

---

## ✅ Lab Completion Checklist

- [ ] Part 1: `cloudflared` installed and version verified
- [ ] Part 2: Python API tunneled — confirmed `CF-Ray` header in response
- [ ] Part 3: Docker Nginx container exposed via tunnel — accessed from mobile
- [ ] Part 4: Minikube/K8s NodePort or port-forward exposed via tunnel
- [ ] Part 5: Webhook receiver registered in GitHub — live push event received
- [ ] Part 6: Read all 5 production gotchas
- [ ] Bonus: Run `cloudflared metrics` and inspect Prometheus output at `:2999`
