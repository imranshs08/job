# Lab 06: Jenkins Active Directory Audit & SIEM Integration

## 🎯 Architecture Objective
In an Enterprise environment, the Security Operations Center (SOC) heavily relies on the Windows Domain Controller's **Event ID 4624 (Successful Logon)** to track user access patterns. However, standard Jenkins deployments utilizing the Active Directory plugin cause "LDAP Blindness"—the Domain Controller only sees the Jenkins Service Account executing blind LDAP queries, rather than seeing the actual interactive user requesting a Kerberos ticket.

**The Solution:** Rather than trying to force the Domain Controller to natively mock a Kerberos event (which requires complex Reverse-Proxy SPN delegation), we will shift left to the **SIEM Layer** (e.g., Splunk, ELK, Datadog). We will install the Jenkins **Audit Trail Plugin** and configure it to stream physical Syslog packets directly to the central Security Information and Event Management (SIEM) dashboard, allowing the SOC to correlate the Jenkins web logins perfectly with standard Windows logs.

---

## Step 1: The Mock Topology Layout (Sandbox Execution)
Instead of heavily provisioning an Azure Windows Server VM and a full Splunk indexer, we will mock these endpoints mathematically:
1. **Mock Domain Controller**: `osixia/openldap` (simulating Active Directory attribute bindings perfectly).
2. **Mock Security Analytics (SIEM)**: We will utilize a barebones `busybox:latest` container configured with Netcat (`nc -lu -p 514`). Netcat will physically rip raw UDP Syslog packets off port 514 and echo them sequentially into `kubectl logs` exactly as Splunk would witness them.

Please save the following strictly as `iam-sandbox.yaml` and apply it (`kubectl apply -f iam-sandbox.yaml`):

```yaml
# 1. The SIEM Splunk Emulator (UDP 514 Log Listener)
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
---
# 2. The Active Directory Emulator (LDAP Port 389)
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

Wait roughly 30 seconds for the images to extract, and verify that both services are reporting `1/1 Running`:
`kubectl get pods -n default`

---

## Step 2: Populating the Mock Domain Controller
We will inject a standard test user (`imran`) natively piped over an LDIF (LDAP Data Interchange Format) payload. Run this execution block verbatim in your terminal:

```bash
kubectl exec -i deploy/mock-ad -n default -- ldapadd -x -D "cn=admin,dc=enterprise,dc=local" -w adminpassword <<EOF
dn: uid=imran,dc=enterprise,dc=local
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
uid: imran
sn: Imran
givenName: H
cn: Imran H
displayName: Imran H
uidNumber: 10000
gidNumber: 10000
userPassword: mysecurepassword
homeDirectory: /home/imran
loginShell: /bin/bash
EOF
```

---

## Step 3: Integrating Jenkins to the Mock Subsystems
Now that our Mock Active Directory and Mock Splunk indexers are running, we must link Jenkins.

1. Port-forward the Jenkins instance: `kubectl port-forward svc/jenkins-svc 8080:8080 -n default`
2. Open your browser and navigate to `http://localhost:8080`.

### Binding Active Directory
1. Go to **Manage Jenkins** ➡️ **Plugins** ➡️ **Available Plugins**.
2. Search for `Audit Trail`. Install the **LDAP** plugin and **Audit Trail** plugin. (Click "Install without restart").
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
4. **Syslog Server Hostname:** `mock-siem-svc` (or `siem-ingest.enterprise.local` for prod)
5. **Port:** `514` (UDP)
6. **Facility:** `AUTH`
7. **Message Name:** `Jenkins`
8. **Message Format:** `RFC3164`
9. Click **Save**.

---

## Step 4: Validating the Architecture (SOC Alerting)
To prove that our new Architecture defeats Domain Controller LDAP Blindness:

1. Open an Incognito Window and access `http://localhost:8080`.
2. Attempt to log in to Jenkins using user `imran` and password `mysecurepassword`.
3. Behind the scenes, Jenkins asks the `osixia/openldap` mock container on port 389 for verification.
4. Jenkins then blasts a Syslog UDP packet to Port 514.
5. In your terminal, check the Mock Splunk indexer:
   ```bash
   kubectl logs deploy/mock-siem -n default
   ```
6. You will see the literal raw UDP packet representing the Interactive Logon hit standard output.

---

## Alternative 1: The Native Bash Audit Exporter (No SIEM Required)
If your organization does not have an active Splunk indexer, route the logs to a text file and natively email them out daily.

### Route Syslog to a Text File
1. Go back to **Manage Jenkins** ➡️ **System** ➡️ **Audit Trail**.
2. Delete the **Syslog Server** logger. Click **Add Logger** ➡️ **Log file**.
3. **Log File Location:** `/var/jenkins_home/logs/audit.log` (Limit 100MB, Count 5). Save.

### The Jenkins Bash Audit Job
1. Create a `Freestyle Project` triggered to **Build periodically** at `H 0 * * *`.
2. Add a **Build Step** ➡️ **Execute shell**:
```bash
#!/bin/bash
TODAY=$(date "+%Y-%m-%d")
REPORT_FILE="active_directory_logins.txt"
echo "=== JENKINS DOMAIN LOGINS FOR $TODAY ===" > $REPORT_FILE
echo "" >> $REPORT_FILE
grep "SUCCESS" /var/jenkins_home/logs/audit.log | grep "$TODAY" >> $REPORT_FILE || echo "No AD Logins tracked today." >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "End of Report." >> $REPORT_FILE
```
3. Attach `active_directory_logins.txt` via **Editable Email Notification** and Save.

---

## Alternative 2: Power-Extracting from the Domain Controller directly
If your architecture firmly mandates that all logs are physically parsed from the Domain Controller itself, Jenkins can act as the Central Automation Orchestrator querying the Windows Server via WinRM!

> [!WARNING]
> ### Platform Restriction: PowerShell `Get-WinEvent` Extraction
> You **must not target the OpenLDAP Linux Sandbox container** with this script. `Get-WinEvent` expects Windows RPC Architecture. To validate this PowerShell artifact explicitly, point the `-ComputerName` variable strictly at a physical Windows Hypervisor (e.g. `localhost` mapped to your workstation domain).

1. Create a `Freestyle Project` executing a Windows batch/PowerShell command:

```powershell
param (
    [string]$DomainController = "DC01.enterprise.local"
)

$Yesterday = (Get-Date).AddDays(-1)
$ReportPath = "${env:WORKSPACE}\DC_Audit_Report.csv"

# Query the physical Domain Controller for Event ID 4624 (Successful Logons)
$AuditLogs = Get-WinEvent -ComputerName $DomainController -FilterHashtable @{LogName="Security"; Id=4624; StartTime=$Yesterday} -ErrorAction SilentlyContinue

# Filter for legitimate Interactive (Type 2) or Network (Type 3) authentications
$ExtractedData = $AuditLogs | Where-Object { $_.Properties[8].Value -eq 2 -or $_.Properties[8].Value -eq 3 } | Select-Object TimeCreated, @{Name="User";Expression={$_.Properties[5].Value}}, @{Name="Source IP";Expression={$_.Properties[18].Value}}

$ExtractedData | Export-Csv -Path $ReportPath -NoTypeInformation
```
2. Attach `DC_Audit_Report.csv` via the Email plugin and Save!

---

## Alternative 3: Dynatrace ActiveGate Log Ingestion (Grail)
Since Dynatrace natively serves as the core monitoring platform in this environment, routing Jenkins Syslog natively into **Dynatrace Log Monitoring v2 (Grail)** is the ultimate unified architectural decision. Dynatrace uniquely allows you to configure your **Environment ActiveGate** as a Syslog Receiver, completely eliminating the need to install a OneAgent directly inside the Jenkins container!

### 1. Enable ActiveGate Syslog Listener
On your physical ActiveGate instance, edit the `custom.properties` file:
```ini
# /var/lib/dynatrace/gateway/config/custom.properties
[collector]
UDPSyslogPort = 514
```
*Restart the ActiveGate service (`systemctl restart dynatracegateway`).*

### 2. Route Jenkins to Dynatrace
1. Inside the Jenkins GUI, go to **Manage Jenkins** ➡️ **System** ➡️ **Audit Trail**.
2. Click **Add Logger** ➡️ **Syslog Server**.
3. **Syslog Server Hostname:** `<YOUR_ACTIVEGATE_IP_ADDRESS>`
4. **Port:** `514`
5. **Facility:** `AUTH`
6. **Message Format:** `RFC3164`
7. Click **Save**.

### 3. Davis AI Log Metric Extraction
Inside the Dynatrace SaaS UI, navigate to **Logs**. You will instantly start receiving the raw Jenkins UDP payloads!
To bind this data directly to the Davis AI engine for intelligent alerting:
1. Go to **Settings** ➡️ **Log Monitoring** ➡️ **Log metrics**.
2. Create a new metric key: `jenkins.auth.success`
3. **Log query:** `content contains "auth: SUCCESS User" AND process.name="Jenkins"`
4. Davis AI will automatically profile this metric over time and generate an alert if anomalous authentication spikes occur outside of standard operational baselines!
