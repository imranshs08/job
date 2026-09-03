# Lab 08: Dynatrace SaaS ActiveGate Syslog Deployment

## Architecture Objective
To validate the **Jenkins Authentication -> Syslog -> Dynatrace Log Monitoring v2** pipeline discussed in Lab 06 physically, we must deploy a true Enterprise Environment ActiveGate into our Minikube cluster. 

Since Dynatrace is proprietary, we will leverage a 30-Day Free SaaS Trial to harvest a valid Tenant URI and PaaS Cryptographic Binding Token. Furthermore, to enable Syslog ingestion natively within a containerized ActiveGate, we will construct a Kubernetes ConfigMap to persistently overwrite the internal `custom.properties` gateway configuration.

---

## Step 1: Harvesting the PaaS Identity
1. Navigate to `dynatrace.com/trial` and instantiate a 30-day Free Tier tenant.
2. Once inside your new dashboard, note your unique Environment URL:
   *(e.g., `https://abc12345.live.dynatrace.com`)*
3. Navigate to **Deploy Dynatrace** -> **Install ActiveGate**.
4. Click **Create Token** to generate your `PaaS Token`. Save this cryptographically secure string!

---

## Step 2: The Infrastructure ConfigMap
By default, the ActiveGate container does not listen for Syslog telemetry. We MUST override its core configuration engine using a standard Kubernetes Volume mount!

Save this locally as `activegate-config.yaml` and apply it:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ag-custom-properties
  namespace: default
data:
  custom.properties: |
    [collector]
    UDPSyslogPort = 514
```
Apply using: `kubectl apply -f activegate-config.yaml`

---

## Step 3: Spinning up the Enterprise ActiveGate
We will pull the official Dynatrace container, bind it to your SaaS tenant, inject the Syslog override ConfigMap, and expose it to Jenkins using a Kubernetes Service.

Save this locally as `activegate-deploy.yaml` (Replace the `<YOUR_TENANT_ID>` and `<YOUR_PAAS_TOKEN>` placeholders!):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynatrace-activegate
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dynatrace-activegate
  template:
    metadata:
      labels:
        app: dynatrace-activegate
    spec:
      containers:
      - name: activegate
        image: dynatrace/activegate
        env:
        - name: DT_TENANT
          value: "https://<YOUR_TENANT_ID>.live.dynatrace.com"
        - name: DT_TOKEN
          value: "<YOUR_PAAS_TOKEN>"
        ports:
        - containerPort: 514
          protocol: UDP
        volumeMounts:
        - name: properties-volume
          mountPath: /var/lib/dynatrace/gateway/config/custom.properties
          subPath: custom.properties
      volumes:
      - name: properties-volume
        configMap:
          name: ag-custom-properties
---
apiVersion: v1
kind: Service
metadata:
  name: dynatrace-activegate-svc
  namespace: default
spec:
  ports:
  - port: 514
    protocol: UDP
  selector:
    app: dynatrace-activegate
```
Apply using: `kubectl apply -f activegate-deploy.yaml`

---

## Step 4: Connecting the Jenkins Pipeline
Once the ActiveGate reports `1/1 Running`, you can complete the architecture we outlined in Lab 06!

1. Open Jenkins GUI (`http://localhost:8080`).
2. Navigate to **Manage Jenkins -> System -> Audit Trail**.
3. Under your **Syslog Server** logger configuration, update the target variables to point directly at your new Kubernetes gateway:
   - **Syslog Server Hostname:** `dynatrace-activegate-svc`
   - **Port:** `514`
4. Click **Save**.

## Step 5: Dashboard Affirmation
Perform an explicit login into Jenkins using the `imran` user matrix we developed in Lab 07. 

Open your browser to your 30-Day Dynatrace Trial URL. Navigate to **Logs**. You will instantly see the UDP payload extracted completely serverlessly across your local container network and bridged straight into the Davis AI SaaS pipeline!
