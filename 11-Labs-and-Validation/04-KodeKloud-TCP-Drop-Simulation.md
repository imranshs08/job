# 🧪 Lab Validation: Free Local TCP Drop Simulation (KodeKloud / Minikube)

> **Scenario:** Proving that an enterprise Rundeck architecture can survive a catastrophic database failure/failover (mimicking Azure SQL Managed Instance maintenance) using a 100% free Kubernetes Sandbox.

This step-by-step guide walks you through deploying a local database, binding Rundeck to it with aggressive JDBC parameters, and violently severing the connection while a job is running to prove the retry/recovery mechanisms.

---

## Step 1: Deploy the Sandbox Database
Instead of paying for Azure SQL, we will spin up a transient PostgreSQL pod inside the cluster.

Create and apply `database.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-svc
  namespace: rundeck
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: rundeck
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_PASSWORD
          value: "mypassword"
```
```bash
kubectl create namespace rundeck
kubectl apply -f database.yaml
```

---

## Step 2: Deploy Rundeck with Defensive JDBC Tuning
Here we inject the critical `socketTimeout=60000` and `tcpKeepAlive=true` parameters into the ConfigMap.

Create and apply `rundeck-sandbox.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rundeck-config
  namespace: rundeck
data:
  rundeck-config.properties: |-
    dataSource.url = jdbc:postgresql://db-svc:5432/postgres?socketTimeout=60000&tcpKeepAlive=true
    dataSource.username = postgres
    dataSource.password = mypassword
    dataSource.testOnBorrow = true
    dataSource.validationQuery = "SELECT 1"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rundeck
  namespace: rundeck
spec:
  replicas: 1
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
        image: rundeck/rundeck:4.17.0
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
```bash
kubectl apply -f rundeck-sandbox.yaml
# Wait for the Rundeck pod to become completely Ready
kubectl get pods -w -n rundeck
```

---

## Step 3: Trigger The Chaos (Simulation)

Once Rundeck is online, log into its GUI via `kubectl port-forward svc/rundeck 4440:4440`, and create a job with a 3-minute sleep loop and a **Retry configuration (Retry: 3, Delay: 1m)**.

**Execute the test exactly in this sequence:**
1. Start the Job in the Rundeck GUI.
2. Open your terminal immediately and aggressively crash the database pod:
   ```bash
   kubectl delete pod -l app=postgres -n rundeck --force --grace-period=0
   ```
   *(This immediately severs the active TCP socket, perfectly mimicking an Azure failover/networking drop).*
3. Watch the Rundeck logs:
   ```bash
   kubectl logs -l app=rundeck -n rundeck -f
   ```

### 🎯 The Expected Result
You will see Rundeck hang for exactly **60 seconds** (dictated by `socketTimeout=60000`). Then, it will throw a violent `SocketTimeoutException` inside the logs and kill the job attempt. 

The scheduler will wait **1 minute** (your configured delay) and automatically retry the job. By that time, the Kubernetes ReplicaSet will have already replaced the dead `postgres` pod. The job will successfully reconnect and finish! You have officially proven enterprise resilience without spending a dime in Azure!
