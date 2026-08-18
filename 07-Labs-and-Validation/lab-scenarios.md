# 🧪 DevOps Validation Labs & Broken Scenarios

> **Objective:** Following tutorials gives the illusion of competence. To truly validate your knowledge and prepare for Senior-level interviews, you must build from scratch without a guide, or fix broken environments. 
> 
> *Rule: You cannot use Google/ChadGPT to copy-paste the answer. You must use official documentation (e.g. docs.docker.com, kubernetes.io).*

---

## 🛑 Phase 1: Linux & AWS Networking Validation
**Lab 1: The "Unreachable Server"**
* **Scenario:** Provision an AWS EC2 instance in a private subnet. Provision a Bastion host in a public subnet. Install Nginx on the private server.
* **Validation Test:** From your local laptop, use SSH agent forwarding to SSH into the Bastion, and then into the private EC2 instance. `curl localhost` to prove Nginx is running.
* **Fail Condition:** You expose the private EC2 instance to the internet, or you copy your private `.pem` key onto the Bastion host (major security violation!).

**Lab 2: Shell Scripting Nightmare**
* **Scenario:** You have a directory of 1,000 log files. Half end in `.log` and half end in `.old`.
* **Validation Test:** Write a single Bash script that finds all `.old` files, archives them into a `tar.gz` file tagged with today's date, deletes the original `.old` files, and streams the output to `/var/log/archive.log`.

---

## 🐳 Phase 2: Containers & Kubernetes Validation
**Lab 3: The "OOMKilled" Deployment**
* **Scenario:** Create a Python/Node memory-leak script that infinitely consumes RAM. Containerize it.
* **Validation Test:** Deploy it to your K8s cluster (Kind/Minikube/EKS). Configure a `resource.limit` of 124Mi. Watch the pod crash. 
* **Proof:** Use `kubectl describe pod` to capture the `OOMKilled` event. Then configure a `LivenessProbe` to restart the pod before it spikes too high.

**Lab 4: Zero-Downtime Rollback**
* **Scenario:** Deploy Nginx 1.14 using a Kubernetes Deployment with 3 replicas. 
* **Validation Test:** Upgrade the image to Nginx 1.19. Watch the RollingUpdate. Oh no, it's a "bad" image (simulate this by picking a non-existent tag like `nginx:1.99`). 
* **Proof:** Run the exact `kubectl rollout undo` command to revert the cluster back to healthy 1.14 seamlessly without external traffic failure.

---

## 🏗️ Phase 3: CI/CD & Terraform Validation
**Lab 5: The Drifted Infrastructure**
* **Scenario:** Use Terraform to map an AWS S3 Bucket and a DynamoDB table (for state locking).
* **Validation Test:** Go into the AWS Console UI and manually delete some tags and change the S3 bucket permissions (making it public instead of private).
* **Proof:** Run `terraform plan`. Observe the infrastructure drift. Run `terraform apply` to forcefully overwrite the manual UI changes back to your strict IaC code baseline.

**Lab 6: The "Broken Build" Pipeline**
* **Scenario:** Set up a Jenkins / GitHub Actions pipeline with three stages: Build, Test, Deploy.
* **Validation Test:** Intentionally break the code in the "Test" stage so it exits with code 1.
* **Proof:** The pipeline must completely stop and fail, and it must trigger an automated Slack/Email alert saying "Build Failed in CI". It should NEVER reach the Deploy phase.

---

## 🔬 Phase 4 & 5: Observability & DevSecOps
**Lab 7: Metric Alert Panic**
* **Scenario:** Install Prometheus and Grafana on your cluster.
* **Validation Test:** Create a custom PromQL metric measuring CPU usage. Use a load-testing tool (like `stress-ng` or `hey`) to spam your cluster with traffic.
* **Proof:** Prove that an Alertmanager alert fires within 1 minute of hitting 80% CPU usage. 

**Lab 8: The Vulnerable Image Fix**
* **Scenario:** Write a Dockerfile using an outdated base image (e.g. `node:10`).
* **Validation Test:** Run `Trivy` or `Snyk` natively via CLI against the image. Capture the high/critical CVEs. 
* **Proof:** Upgrade the Dockerfile base image to a secure, Alpine-based tag. Rerun the scan to prove 0 critical vulnerabilities before pushing to DockerHub.
