# 🧪 Senior DevOps Validation Labs & Interview Scenarios

> **Objective:** Following tutorials gives the illusion of competence. To truly validate your knowledge and prepare for Senior-level interviews, you must build from scratch without a guide, or fix broken environments. 
> 
> *Rule: You cannot use Google/ChatGPT to copy-paste the answer. You must use official documentation. These scenarios represent the most commonly asked technical interview questions for 2026/2027.*

---

## 🛑 Phase 1A: Linux Internal & Troubleshooting
**Lab 1: The "Disk is Full but Not Full" Panic**
* **Interview Question:** "A developer says they cannot write to `/var/log`, but when you run `df -h`, it shows 50% free space. What is wrong and how do you fix it?"
* **Validation Lab:** Fill up all inodes on a Linux virtual machine without filling up disk block space (`touch file_{1..1000000}`). Prove that `df -i` shows 100% capacity while `df -h` shows plenty. Fix it by finding and securely deleting the empty files using `find`.

**Lab 2: The Zombie Process Swarm**
* **Interview Question:** "Your server load is extremely high. You see a bunch of processes marked as `<defunct>`. How do you kill a zombie process?"
* **Validation Lab:** Write a malicious C program or bash script that forcefully creates Zombie processes. Verify they appear in `top` and `ps aux | grep 'Z'`. 
* **Proof:** Prove you know you *cannot* `kill -9` a zombie. Find the parent process ID (PPID) using `ps -eo pid,ppid,stat,cmd`, and kill the parent process to reap the zombies.

**Lab 3: The Broken SSH Key Exchange**
* **Interview Question:** "A user cannot SSH into a machine. They are getting 'Permission Denied (publickey)'. Walk me through your troubleshooting steps."
* **Validation Lab:** Intentionally break your `~/.ssh/authorized_keys` file by changing its permissions to `777`. Observe the SSH failure. Validate the fix by running SSH in verbose mode (`ssh -vvv`) on the client, reviewing `/var/log/auth.log` on the server, and resetting permissions precisely to `600` and `700` for the directory.

---

## 🛑 Phase 1B: AWS Networking & Architecture
**Lab 4: The 3-Tier VPC Architecture from Scratch**
* **Interview Question:** "Design a highly available 3-tier VPC in AWS. Which subnets get public IPs? Where does the Database sit?"
* **Validation Lab:** Provision from scratch via AWS CLI/Console: 1 VPC, 2 Public Subnets (Web), 2 Private Subnets (App), 2 Protected Subnets (DB) across 2 Availability Zones.
* **Proof:** Deploy an EC2 in the App subnet. Give the App subnet a NAT Gateway so it can update its packages, but prove it cannot be accessed directly from the Internet.

---

## 🐳 Phase 2: Containers & Kubernetes (CKA Focus)
**Lab 5: The "OOMKilled" Mystery**
* **Interview Question:** "Your pod keeps restarting and shows OOMKilled. How do you stop this from happening?"
* **Validation Lab:** Create a Python memory-leak script. Containerize it. Deploy it to K8s. Configure a `resources.limits.memory` of 124Mi. Watch the pod crash. 
* **Proof:** Use `kubectl describe pod` to capture the `OOMKilled` event. Then configure a memory request/limit appropriately and add a `LivenessProbe`.

**Lab 6: Zero-Downtime Rollback**
* **Interview Question:** "You deployed a new version of your app and the whole site went down. How do you revert it instantly?"
* **Validation Lab:** Deploy Nginx 1.14 using a Kubernetes Deployment with 3 replicas. Upgrade the image to a non-existent tag like `nginx:1.99`. Watch the environment hang.
* **Proof:** Run `kubectl rollout history` and `kubectl rollout undo` to revert seamlessly without external traffic failure.

**Lab 7: CrashLoopBackOff Diagnosis**
* **Interview Question:** "What does CrashLoopBackOff mean and what are the top 3 reasons it happens?"
* **Validation Lab:** Write a Dockerfile with a broken `CMD` standard entrypoint (e.g., executing a script that doesn't have bash `x` permissions). Deploy to cluster.
* **Proof:** Use `kubectl logs --previous` and `kubectl get events` to pinpoint the exact permission denied output.

**Lab 8: Kube-DNS Failure**
* **Interview Question:** "Two microservices in different namespaces cannot communicate via their service names. Why?"
* **Validation Lab:** Deploy App A in `namespace-a` and DB in `namespace-b`. Attempt to `curl db-service:5432` from App A. Watch it fail. 
* **Proof:** Demonstrate your FQDN knowledge by changing the connection string to `db-service.namespace-b.svc.cluster.local`. 

---

## 🏗️ Phase 3A: Terraform State & Drift
**Lab 9: The Drifted Infrastructure**
* **Interview Question:** "Someone manually changed a Security Group in the AWS console. Does Terraform know? How do you fix it?"
* **Validation Lab:** Provision a Security Group via Terraform allowing port 80. Go into AWS Console and manually add port 443.
* **Proof:** Run `terraform plan`. Observe the infrastructure drift. Run `terraform apply` to forcefully aggressively overwrite the manual UI change back to port 80.

**Lab 10: State File Lock Hijack**
* **Interview Question:** "You run terraform apply but it tells you the state is locked. The developer who locked it went on vacation. What do you do?"
* **Validation Lab:** Hook Terraform to a remote S3 backend with DynamoDB locking. Force kill a terraform process mid-apply so the lock persists in DynamoDB.
* **Proof:** Run `terraform force-unlock <LOCK_ID>` explicitly to kill the lock and resume control safely.

---

## 🚀 Phase 3B: CI/CD Pipeline Horrors
**Lab 11: The Secret Leak in Jenkins/GitHub Actions**
* **Interview Question:** "How do you securely pass AWS credentials to your CI/CD pipeline without hardcoding them in the Jenkinsfile?"
* **Validation Lab:** Build a Jenkinsfile that pushes an image to AWS ECR. 
* **Fail Condition:** You write `AWS_ACCESS_KEY_ID="xxxxx"` in the pipeline script.
* **Proof:** Use Jenkins Credentials Binding plugin OR GitHub Actions AWS OIDC provider (OpenID Connect) to assume a temporary IAM role and authenticate securely. 

---

## 🐍 Phase 4: API & Python Automation
**Lab 12: The Boto3 Orphan Destroyer**
* **Interview Question:** "Engineers keep spinning up EC2 instances and abandoning them. How do you save us money?"
* **Validation Lab:** Write a Python Boto3 script that scans all regions for EBS Volumes with state `Available` (meaning they are detached from any EC2 instance).
* **Proof:** The script should calculate the total Gigabytes wasted and prompt the user "Do you want to delete these? (y/n)". If yes, it iterates and deletes the volumes. 

---

## 🔬 Phase 5: Prometheus Observability
**Lab 13: Metric Alert Panic (PromQL)**
* **Interview Question:** "How do you alert me only if CPU hits 90% for more than 5 minutes consistently?"
* **Validation Lab:** Install Prometheus/Grafana. Write the PromQL: `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90`.
* **Proof:** Use `stress-ng` to blast your CPU momentarily for 1 minute. Prove that Alertmanager *does not* fire. Keep the stress up for 6 minutes. Prove Alertmanager *does* fire to Slack.
