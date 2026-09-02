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
```

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

**Test Execution:**
1. Start a long-running, looping job in Rundeck via the GUI (e.g. A bash script that echoes numbers every 5 seconds for 5 minutes).
2. During the job execution, initiate a manual SQL MI failover using the Azure CLI:
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
If you have configured **Job Retries** in the Rundeck GUI (e.g., Retry 3 times, Delay 1 minute), the Rundeck scheduler will cleanly restart the job 1 minute later, completely bypassing the maintenance interruption.
