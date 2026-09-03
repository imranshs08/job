# Lab 06: Jenkins Active Directory Audit & SIEM Integration

## 🎯 Architecture Objective
In an Enterprise environment, the Security Operations Center (SOC) heavily relies on the Windows Domain Controller's **Event ID 4624 (Successful Logon)** to track user access patterns. However, standard Jenkins deployments utilizing the Active Directory plugin cause "LDAP Blindness"—the Domain Controller only sees the Jenkins Service Account executing blind LDAP queries, rather than seeing the actual interactive user requesting a Kerberos ticket.

**The Solution:** Rather than trying to force the Domain Controller to natively mock a Kerberos event (which requires complex Reverse-Proxy SPN delegation), we will shift left to the **SIEM Layer** (e.g., Splunk, ELK, Datadog). We will install the Jenkins **Audit Trail Plugin** and configure it to stream physical Syslog packets directly to the central Security Information and Event Management (SIEM) dashboard, allowing the SOC to correlate the Jenkins web logins perfectly with standard Windows logs.

---

## Step 1: Mitigating the Vulnerability (Plugin Installation)
We will leverage the official Audit Trail engine.

1. Navigate to **Manage Jenkins** ➡️ **Plugins** ➡️ **Available plugins**.
2. Search for: `Audit Trail`.
3. Select the plugin and click **Install without restart**.

*(Note: If you are building Immutable Controllers as per Lab 05, you would simply add `audit-trail:3.13` to your `plugins.txt` baseline instead of installing it manually!)*

---

## Step 2: Configuring the Syslog Stream
Once installed, we must route the internal Java logging engine out to the remote SIEM server.

1. Navigate to **Manage Jenkins** ➡️ **System**.
2. Scroll to the bottom to find the **Audit Trail** configuration section.
3. Click **Add Logger** ➡️ **Syslog Server**.
4. In the configuration block, enter your Enterprise SIEM endpoints:
   - **Syslog Server Hostname:** `siem-ingest.enterprise.local` (or `127.0.0.1` for local testing)
   - **Port:** `514` (UDP) or `6514` (TLS TCP)
   - **Facility:** `AUTH` or `DAEMON`
   - **Message Format:** Standard RFC3164 (or RFC5424 if supported by your SIEM).

---

## Step 3: SOC Validation & Alerting
When a user attempts to login to Jenkins, the local LDAP Bind occurs natively, but immediately afterward, Jenkins will blast a UDP/TCP packet to your SIEM containing the exact string:

`Aug 18 14:12:44 jenkins-controller auth: SUCCESS User imran.h authenticated from 192.168.1.100`

### Splunk / SIEM Correlation Rule:
Your SOC team will construct a dashboard merging your Active Directory `Windows Event ID 4624` logs with your Jenkins `Syslog Facility AUTH` logs:
```spl
index=iam (sourcetype=wineventlog:security EventCode=4624) OR (sourcetype=syslog host=jenkins-controller auth)
| eval MergedUser=coalesce(Account_Name, extract(user))
| stats count by MergedUser, host
```
