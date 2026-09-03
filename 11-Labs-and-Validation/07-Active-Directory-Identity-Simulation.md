# Lab 07: Active Directory Simulation & Identity Execution

## 🎯 Architecture Objective
After deploying our Mock IAM topology in Lab 06 (the `mock-ad` Domain Controller and `mock-siem` UDP Logger), we must functionally populate it with identity data. 

In a physical enterprise, a Systems Administrator uses the "Active Directory Users and Computers" MMC snap-in to create users. Because we are simulating AD computationally inside a Linux OpenLDAP pod, we will forcefully inject Directory Objects using an **LDIF (LDAP Data Interchange Format)** payload over `bash` native pipes.

---

## Step 1: Populating the Mock Domain Controller
We will inject a standard test user (`imran`) natively.

1. Ensure the `mock-ad` pod is dynamically running from Lab 06 (`kubectl get pods`).
2. Run this execution block verbatim in your terminal:
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
*If successful, it returns: `adding new entry "uid=imran,dc=enterprise,dc=local"`*

---

## Step 2: Simulating Distributed Linux Logins
To simulate a network node (like a Dynatrace active gate or standard Linux App Server) cross-authenticating to your domain:

1. Spin up a transient Linux pod simulating an external server:
   ```bash
   kubectl run mock-linux-server -it --image=ubuntu --rm -- bash
   ```
2. Once dropped into the root prompt of the remote server, execute:
   ```bash
   apt-get update && apt-get install -y ldap-utils
   ldapwhoami -x -D "uid=imran,dc=enterprise,dc=local" -w mysecurepassword -H ldap://mock-ad-svc:389
   ```
*Observation: The server connects port 389 cryptographically validating the user against the DC. This represents true Network/Interactive execution without web forms!*

---

## Step 3: Simulating the Jenkins Pipeline Login
Now simulate the problematic "LDAP Web Blindness" vector using the infrastructure we built in Lab 06.

1. Port forward Jenkins: `kubectl port-forward svc/jenkins-svc 8080:8080 -n default`.
2. Access `http://localhost:8080` in an Incognito layout.
3. Authenticate strictly using `imran` and `mysecurepassword`.
4. Validate the **SIEM Bridge**:
   ```bash
   kubectl logs deploy/mock-siem -n default
   ```
The raw `AUTH SUCCESS` UDP packet will dynamically cascade across your terminal, proving you successfully integrated IAM into your Logging aggregator!

---

> [!WARNING]
> ### Platform Restriction: PowerShell `Get-WinEvent` Extraction
> If you are attempting to test the native PowerShell **DC Extractor Jenkins Script** formulated in the previous module, you **must not target this OpenLDAP container**. `Get-WinEvent` expects Windows RPC (Remote Procedure Call) Architecture and `.evtx` logic. To validate the PowerShell artifact explicitly, point the `-ComputerName` variable strictly at a physical Windows Hypervisor (e.g. `localhost` mapped to your workstation domain).
