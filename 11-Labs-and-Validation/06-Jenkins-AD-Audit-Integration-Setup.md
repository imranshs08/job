# Lab 06: Local IAM Sandbox Execution

In the previous theory document, we discovered the LDAP authentication bypass that prevents traditional Windows auditing frameworks from recording Jenkins user logins natively, and proposed mapping the Jenkins Audit payload directly into the Syslog ingestion layer.

To fundamentally prove this architecture inside your localhost environment, we will dynamically scaffold a highly lightweight rendition of a Fortune 500 network utilizing two sub-10MB Cloud-Native microservices.

---

## Step 1: The Mock Topology Layout
Instead of heavily provisioning an Azure Windows Server VM and a full 8GB Splunk indexer, we will mock these endpoints mathematically:
1. **Mock Domain Controller**: `osixia/openldap` (simulating Active Directory attribute bindings perfectly).
2. **Mock Security Analytics (SIEM)**: We will utilize a barebones `busybox:latest` container configured with Netcat (`nc -lu -p 514`). Netcat will physically rip raw UDP Syslog packets off port 514 and echo them sequentially into `kubectl logs` exactly as Splunk would witness them.

---

## Step 2: Provisioning the Environment 
Execute the configuration by mapping this manifest into Kubernetes. 

Please save the following strictly as `iam-sandbox.yaml`:
```yaml
# ----------------------------------------------------
# 1. The SIEM Splunk Emulator (UDP 514 Log Listener)
# ----------------------------------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mock-siem
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mock-siem
  template:
    metadata:
      labels:
        app: mock-siem
    spec:
      containers:
      - name: mock-siem
        image: busybox:latest
        command: ["nc", "-lu", "-p", "514"]
---
apiVersion: v1
kind: Service
metadata:
  name: mock-siem-svc
  namespace: default
spec:
  ports:
  - port: 514
    protocol: UDP
  selector:
    app: mock-siem

# ----------------------------------------------------
# 2. The Active Directory Emulator (LDAP Port 389)
# ----------------------------------------------------
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mock-ad
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mock-ad
  template:
    metadata:
      labels:
        app: mock-ad
    spec:
      containers:
      - name: mock-ad
        image: osixia/openldap:1.5.0
        env:
        - name: LDAP_ORGANISATION
          value: "Enterprise"
        - name: LDAP_DOMAIN
          value: "enterprise.local"
        - name: LDAP_ADMIN_PASSWORD
          value: "adminpassword"
---
apiVersion: v1
kind: Service
metadata:
  name: mock-ad-svc
  namespace: default
spec:
  ports:
  - port: 389
  selector:
    app: mock-ad
```

Apply it into the cluster natively:
```bash
kubectl apply -f iam-sandbox.yaml
```

Wait roughly 30 seconds for the images to extract, and verify that both services are reporting `1/1 Running`:
```bash
kubectl get pods -n default
```

Once running, we will re-configure your Jenkins Security Administration to validate against `mock-ad-svc` instead of the internal realm, proving 100% active parity!
