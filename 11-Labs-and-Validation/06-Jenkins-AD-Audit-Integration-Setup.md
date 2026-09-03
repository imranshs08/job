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


---

## Step 3: Integrating Jenkins to the Mock Subsystems
Now that our Mock Active Directory and Mock Splunk indexers are running, we must link Jenkins.

1. Port-forward the Jenkins instance: `kubectl port-forward svc/jenkins-svc 8080:8080 -n default`
2. Open your browser and navigate to `http://localhost:8080`.

### Binding Active Directory
1. Go to **Manage Jenkins** ➡️ **Plugins** ➡️ **Available Plugins**.
2. Install the **LDAP** plugin and **Audit Trail** plugin. (Click "Install without restart").
3. Go to **Manage Jenkins** ➡️ **Security**.
4. Under `Security Realm`, click the dropdown and choose **LDAP**.
5. **Server:** `ldap://mock-ad-svc:389`
6. **root DN:** `dc=enterprise,dc=local`
7. **Manager DN:** `cn=admin,dc=enterprise,dc=local`
8. **Manager Password:** `adminpassword`
9. Click **Test LDAP settings**. It should say `Success!`. Click **Save**.

### Binding the Syslog SIEM
1. Go to **Manage Jenkins** ➡️ **System**.
2. Scroll to the bottom to **Audit Trail**.
3. Click **Add Logger** ➡️ **Syslog Server**.
4. **Syslog Server Hostname:** `mock-siem-svc`
5. **Port:** `514`
6. **Facility:** `AUTH`
7. **Message Name:** `Jenkins`
8. **Message Format:** `RFC3164`
9. Click **Save**.

---

## Step 4: Validating the Architecture
To prove that our new Architecture defeats Domain Controller LDAP Blindness:

1. Open an Incognito Window and access `http://localhost:8080`.
2. Attempt to log in to Jenkins.
3. Behind the scenes, Jenkins asks the `osixia/openldap` mock container on port 389 for verification.
4. Jenkins then blasts a Syslog User trace off to Port 514 UDP.
5. In your terminal, check the Mock Splunk indexer:
   ```bash
   kubectl logs deploy/mock-siem -n default
   ```
6. You will see the literal raw UDP packet representing the Interactive Logon hit standard output! We have successfully pushed Identity context layer parsing out to the SIEM boundary!


---

## Alternative Step 4: The Native Bash Audit Exporter (No SIEM Required)
If your organization does not have an active Splunk or Syslog indexer, you can natively retain these logs and dispatch them over Email via a scheduled Jenkins Job!

### A. Route Syslog to a Text File
Instead of routing the Audit Trail to `Syslog Server`, route it physically to the Jenkins hard drive.
1. Go back to **Manage Jenkins** ➡️ **System** ➡️ **Audit Trail**.
2. Delete the **Syslog Server** logger.
3. Click **Add Logger** ➡️ **Log file**.
4. **Log File Location:** `/var/jenkins_home/logs/audit.log`
5. **Limit:** `100MB`, **Count:** `5`.
6. Click **Save**.

### B. The Jenkins Bash Audit Job
Now, we dynamically query this file daily and email it to the Admins.
1. Create a `Freestyle Project` named `AD-Audit-Daily-Report`.
2. Under **Build Triggers**, select **Build periodically** and enter `H 0 * * *` (runs every midnight).
3. Add a **Build Step** ➡️ **Execute shell**:

```bash
#!/bin/bash
# Fetch todays Date physically matching the Audit format
TODAY=$(date "+%Y-%m-%d")
REPORT_FILE="active_directory_logins.txt"

echo "=== JENKINS DOMAIN LOGINS FOR $TODAY ===" > $REPORT_FILE
echo "" >> $REPORT_FILE

# Grep out the exact successes from the Audit File securely generated by Jenkins
grep "SUCCESS" /var/jenkins_home/logs/audit.log | grep "$TODAY" >> $REPORT_FILE || echo "No AD Logins tracked today." >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "End of Report." >> $REPORT_FILE
```

### C. Configure The Email Notification
1. Under **Post-build Actions**, click **Editable Email Notification**.
2. **Project Recipient List:** `security-team@enterprise.local`
3. **Subject:** `Jenkins AD Audit Logs - $BUILD_ID`
4. **Attachments:** `active_directory_logins.txt`
5. Click **Save** and trigger a test execution! 

This achieves perfect compliance reporting, isolating the Active Directory footprint without requiring a centralized logging environment!
