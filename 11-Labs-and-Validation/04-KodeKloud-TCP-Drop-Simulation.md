# 🧪 Lab Validation: Free Local TCP Drop Simulation (KodeKloud / Minikube)

> **Scenario:** Proving that an enterprise Rundeck architecture can survive a catastrophic database failure/failover (mimicking Azure SQL Managed Instance maintenance) using a 100% free Kubernetes Sandbox.

This step-by-step guide walks you through deploying a local database, binding Rundeck to it with aggressive JDBC parameters, and violently severing the connection while a job is running to prove the retry/recovery mechanisms.

---

## 💻 Pre-requisite: Local Windows Sandbox Setup (Minikube)
If you do not have an active KodeKloud workspace, you can spin up this exact Kubernetes cluster securely on your local Windows PC. Open **PowerShell as Administrator** and execute:

```powershell
# 1. Install Minikube and Kubernetes CLI via Windows Package Manager
winget install minikube
winget install Kubernetes.kubectl

# 2. Start the Minikube cluster (Docker Desktop must be running)
minikube start --driver=docker --memory=4096 --cpus=2

# 3. Verify the cluster is running
kubectl get nodes
```
*(Once your node says `Ready`, you can proceed to Step 1 below!)*

---

## Step 1: Deploy the Sandbox Database
Instead of paying for Azure SQL, we will spin up a transient PostgreSQL pod inside the cluster.

Create and apply `database.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-svc # The internal cluster DNS name Rundeck will use to connect
  namespace: rundeck
spec:
  ports:
  - port: 5432 # Standard PostgreSQL port
  selector:
    app: postgres # Routes traffic to our DB pod
---
apiVersion: v1
kind: Service
metadata:
  name: rundeck
  namespace: rundeck
spec:
  ports:
  - port: 4440
  selector:
    app: rundeck
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
        image: postgres:15-alpine # Lightweight Alpine image for fast lab provisioning
        env:
        - name: POSTGRES_PASSWORD
          value: "mypassword" # Hardcoded for lab purposes only
```
```bash
kubectl create namespace rundeck
kubectl apply -f database.yaml
```

---

## Step 2: Deploy Rundeck with Defensive JDBC Tuning

### Create Kubernetes Secret (Security Best Practice)
Create and apply `rundeck-secret.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rundeck-secrets
  namespace: rundeck
type: Opaque
data:
  # Generate this placeholder by running in terminal: echo -n 'abcd efgh ijkl mnop' | base64
  SMTP_APP_PASSWORD: <BASE64_ENCODED_APP_PASSWORD_PLACEHOLDER> 
```

### Create Rundeck Deployment (Env Var Configuration)
Create and apply `rundeck-sandbox.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rundeck
  namespace: rundeck
spec:
  ports:
  - port: 4440
  selector:
    app: rundeck
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
        env:
        # --- GUI Access Route ---
        - name: RUNDECK_GRAILS_URL
          value: "http://localhost:4440"

        # --- Critical TCP Resilience Parameters ---
        - name: RUNDECK_DATABASE_URL
          value: "jdbc:postgresql://db-svc:5432/postgres?socketTimeout=60000&tcpKeepAlive=true"
        - name: RUNDECK_DATABASE_USERNAME
          value: "postgres"
        - name: RUNDECK_DATABASE_PASSWORD
          value: "mypassword"
        
        # --- FREE SMTP Email Notifications (via Gmail) ---
        - name: RUNDECK_GRAILS_MAIL_HOST
          value: "smtp.gmail.com"
        - name: RUNDECK_GRAILS_MAIL_PORT
          value: "587"
        - name: RUNDECK_GRAILS_MAIL_USERNAME
          value: "imranshs08@gmail.com"
        - name: RUNDECK_GRAILS_MAIL_DEFAULT_FROM
          value: "imranshs08@gmail.com"
        - name: RUNDECK_GRAILS_MAIL_PROPS_MAIL_SMTP_STARTTLS_ENABLE
          value: "true"
        - name: RUNDECK_GRAILS_MAIL_PROPS_MAIL_SMTP_AUTH
          value: "true"
        - name: SMTP_APP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rundeck-secrets
              key: SMTP_APP_PASSWORD
        - name: RUNDECK_GRAILS_MAIL_PASSWORD
          value: "$(SMTP_APP_PASSWORD)"
```
```bash
kubectl apply -f rundeck-sandbox.yaml
# Wait for the Rundeck pod to become completely Ready
kubectl get pods -w -n rundeck
```

Once Rundeck is online, log into its GUI via `kubectl port-forward svc/rundeck 4440:4440`. 

### Step 2.5: Create the Validation Job
You can manually click through the GUI, or you can import this exact Rundeck Job YAML into your project to deploy the resilience tester.

Create a file called `failover-test-job.yaml` and upload it to Rundeck:
```yaml
- defaultTab: nodes
  description: Simulates a long-running task to test TCP connection resilience during an Azure SQL MI failover.
  executionEnabled: true
  id: kodekloud-failover-test
  loglevel: INFO
  name: Database Resilience Tester
  nodeFilterEditable: false
  notification:
    onfailure:
      email:
        recipients: imranshs08@gmail.com
        subject: "[ALERT] Rundeck Azure SQL Connectivity Failure"
    onretryablefailure:
      email:
        recipients: imranshs08@gmail.com
        subject: "[RETRY] Rundeck TCP KeepAlive triggered automated Retry"
  retry:
    delay: 1m
    retry: 3
  scheduleEnabled: true
  sequence:
    commands:
    - script: |
        #!/bin/bash
        STATE_FILE="/tmp/rundeck_job_state.txt"
        START_POINT=1

        # IDEMPOTENCY CHECK: Did the DB failover crash us halfway through?
        # If so, we read the state file and resume exactly where we left off!
        if [ -f "$STATE_FILE" ]; then
          START_POINT=$(cat $STATE_FILE)
          echo "[IDEMPOTENCY TRIGGERED] Resuming job from previous failure point at heartbeat $START_POINT!"
        else
          echo "[START] Initiating fresh resilience test..."
        fi

        for i in $(seq $START_POINT 100); do
          echo "Simulating work... heartbeat $i"
          echo $i > $STATE_FILE # Save our state constantly
          sleep 5
        done
        
        # Cleanup state upon true completion
        rm -f $STATE_FILE
        echo "[SUCCESS] Test definitively completed. State wiped."
    keepgoing: false
    strategy: node-first
```

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
