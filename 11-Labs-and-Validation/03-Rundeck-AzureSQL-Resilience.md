# 💼 Business Case: Rundeck Resilience on AKS (Azure SQL MI Maintenance)

> **Scenario:** Rundeck jobs hang and fail hours later during backend Azure SQL Managed Instance maintenance due to "Silent TCP Drops / Half-Open Sockets". 

This operational runbook provides the exact Terraform provisioning requirements, the JVM/JDBC configuration changes, and the exact commands to validate the architecture under simulated failure.

---

## 🏗️ Phase 1: Resource Provisioning (Terraform/CLI)

Ensure the Azure SQL Managed Instance (MI) and AKS clusters are provisioned properly inside the same or peered VNets.

**Fast Provisioning snippet (Azure CLI):**
```bash
# 1. Create AKS Cluster
az aks create \
  --resource-group rg-devops \
  --name aks-rundeck-prod \
  --node-vm-size Standard_DS2_v2 \
  --node-count 3 \
  --generate-ssh-keys

# 2. Extract AKS credentials to local Kubeconfig
az aks get-credentials --resource-group rg-devops --name aks-rundeck-prod

# 3. Provision Azure SQL MI (Usually takes up to 4 hours in reality)
# Note: Ensure the VNet/Subnet is correctly delegated for SQL MI
az sql mi create \
  --resource-group rg-devops \
  --name sqlmi-rundeck-backend \
  --subnet /subscriptions/.../subnets/sql-subnet \
  --admin-user dbadmin \
  --admin-password 'ComplexPassword123!'
```

---

## 🔧 Phase 2: Configuration (The Fix)

The root cause of silent connection drops is Java's default indefinite wait time for TCP packets. When Azure fails over the database, Java doesn't know. 

### Step 1: Update Rundeck ConfigMap or Secret
You must inject aggressive timeout settings into the JDBC driver.

Create or update the `rundeck-config.yaml` Kubernetes manifest:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rundeck-config
  namespace: rundeck
data:
  rundeck-config.properties: |-
    # Aggressive Socket Timeouts & TCP KeepAlive
    dataSource.url = jdbc:sqlserver://sqlmi-rundeck-backend.database.windows.net:1433;databaseName=rundeck;socketTimeout=60000;loginTimeout=30;tcpKeepAlive=true
    
    # HikariCP Connection Validation (Test on Borrow)
    dataSource.testOnBorrow = true
    dataSource.validationQuery = "SELECT 1"
    
    # Ensure connections don't live longer than Azure's gateway TCP idle timeout (10 mins)
    dataSource.maxLifetime = 600000 

    # --- FREE SMTP Email Notifications (via Gmail) ---
    grails.mail.host = smtp.gmail.com
    grails.mail.port = 587
    grails.mail.username = imranshs08@gmail.com
    grails.mail.password = your-16-char-app-password
    grails.mail.default.from = imranshs08@gmail.com
    # Required for Gmail's TLS enforcement:
    grails.mail.props.mail.smtp.starttls.enable = true
    grails.mail.props.mail.smtp.auth = true
```

> **🔑 How to generate your Gmail App Password:**
> Google no longer allows plain-text passwords in external apps. To get your 16-character password:
> 1. Go to your **Google Account -> Security**.
> 2. Ensure **2-Step Verification** is turned ON.
> 3. Search for **App Passwords** and create one named "Rundeck AKS".
> 4. Paste the 16-character string into `grails.mail.password` above (no spaces).

### Step 1.5: Rundeck Deployment (The Image & Mounting)
To deploy Rundeck into AKS, you must use the official Docker image and map the ConfigMap you just created into the container's configuration path.

Create `rundeck-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rundeck
  namespace: rundeck
spec:
  replicas: 1 # Rundeck clustered mode is a paid enterprise feature; open-source usually runs as a single robust replica
  selector:
    matchLabels:
      app: rundeck
  template:
    metadata:
      labels:
        app: rundeck
    spec:
      containers:
      - name: rundeck
        image: rundeck/rundeck:4.17.0 # Pin your image tag in production!
        ports:
        - containerPort: 4440
        volumeMounts:
        - name: rundeck-config-volume
          mountPath: /home/rundeck/server/config/rundeck-config.properties
          subPath: rundeck-config.properties
      volumes:
      - name: rundeck-config-volume
        configMap:
          name: rundeck-config
```
*Note: We use the `subPath` volume mount trick here so we can inject only the properties file without overwriting the entire default `/home/rundeck/server/config/` directory!*

### Step 2: Apply the Configuration and Rollout
```bash
# 1. Apply the new config map
kubectl apply -f rundeck-config.yaml

# 2. Trigger a zero-downtime rolling restart of the Rundeck pods to pick up the new driver settings
kubectl rollout restart deployment rundeck -n rundeck

# 3. Monitor the rollout to ensure the pods start cleanly
kubectl rollout status deployment rundeck -n rundeck
```

---

## 🚨 Phase 3: Simulated Validation

To prove that the connection drops are handled gracefully by Rundeck, you can force a manual failover on the Azure SQL MI via the portal or CLI, and simultaneously watch the Rundeck pod logs.

### Step 1: Create the Rundeck Validation Job
You can manually click through the GUI, or you can simply import this exact Rundeck Job YAML into your project to deploy the resilience tester.

Create a file called `failover-test-job.yaml` and upload it to Rundeck:
```yaml
- defaultTab: nodes
  description: Simulates a long-running task to test TCP connection resilience during an Azure SQL MI failover.
  executionEnabled: true
  id: azure-failover-test
  loglevel: INFO
  name: Database Resilience Tester
  nodeFilterEditable: false
  notification:
    onfailure:
      email:
        recipients: imranshs08@gmail.com
        subject: "🚨 Rundeck Azure SQL Connectivity Failure Alert"
    onretry:
      email:
        recipients: imranshs08@gmail.com
        subject: "🔄 Rundeck TCP KeepAlive triggered automated Retry"
  retry:
    delay: 1m
    retry: 3
  scheduleEnabled: true
  sequence:
    commands:
    - exec: |
        echo "Starting resilience test..."
        for i in {1..100}; do
          echo "Simulating work... heartbeat $i"
          sleep 5
        done
        echo "Test completed locally."
    keepgoing: false
    strategy: node-first
```
*Note the `retry` block! This is what ensures Rundeck tries again 1 minute later after the 60-second TCP KeepAlive successfully kills the dead database connection lock!*

### Step 2: Test Execution & Failover
1. Run the `Database Resilience Tester` job inside Rundeck. It will run for roughly 8 minutes.
2. While the job is running (around heartbeat 10), initiate a manual SQL MI failover using the Azure CLI:
```bash
az sql mi failover \
  --resource-group rg-devops \
  --name sqlmi-rundeck-backend
```
3. Immediately follow the logs of the Rundeck pod:
```bash
kubectl logs -l app=rundeck -n rundeck -f
```

**Expected Result (Success):**
Instead of hanging for 4 hours, within **exactly 60 seconds**, the Rundeck pod will throw a `SocketTimeoutException`. The HikariCP connection pool will instantly shred the dead JDBC connections.
The Rundeck scheduler will recognize the failure, apply the native Job Retry logic, and cleanly restart the job 1 minute later (connecting to the newly stabilized Azure SQL secondary instance), completely bypassing the maintenance outage!

---

## 🌩️ Real-World Interview & Business Case Deep Dive

If you need to defend this architecture in a systems design interview or to a principal engineer, cite these **three classic cloud failures** that this runbook prevents:

### 1. The "4-Minute Idle" TCP Drop (Most Common)
Azure's underlying physical networking load balancers have a hardcoded rule: **If a TCP connection is completely silent for 4 minutes, Azure silently cuts the wire.**
*   **The Threat:** A Rundeck job connects to the database to log its state. It then executes a heavy bash script on a remote server taking 5 minutes. When it finishes, it tries to write "I succeeded!" to the database. Because the connection was silent for 5 minutes, Azure already dropped it. The job crashes at the very end.
*   **The Defense:** The `tcpKeepAlive=true` parameter forces Linux to send invisible network "heartbeats" every 60 seconds. Azure sees the packets and never drops the connection.

### 2. The "Ghost State" Transaction Rollback
When Azure performs monthly patching, it forcefully shuts down the Primary SQL node and promotes a Secondary node.
*   **The Threat:** If a Rundeck job is halfway through a massive database transaction (e.g., inserting 10,000 logs), the failover instantly kills it. The database totally **rolls back** those logs to protect data integrity. Rundeck marks the job as `FAILED`, but the bash script it triggered might have actually completed successfully on the external server!
*   **The Defense:** This is exactly why we configure **Job Retries** and emphasize **Idempotency**. When the job automatically restarts 1 minute later, the bash script must be smart enough to say "I already completed this work" rather than blindly running it twice and destroying the server.

### 3. The Java DNS Caching Nightmare
When Azure SQL MI fails over, the underlying backend IP address changes. Azure updates its virtual DNS instantaneously.
*   **The Threat:** Rundeck is built on the Java JVM. By default, older Java versions **cache DNS records indefinitely**. Rundeck will blindly keep trying to connect to the old, dead IP address for hours, throwing `Connection Refused` errors, completely unaware that Azure moved the database!
*   **The Defense:** Set `networkaddress.cache.ttl=60` inside the `java.security` configuration file on the Rundeck container. This forces Java to wipe its DNS memory every 60 seconds and gracefully ask Azure for the new IP address.
