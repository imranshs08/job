# 📘 Day-32 - How to Manage Hundreds of Kubernetes Clusters ??? - KOPS

## 🎯 The "Why" (Core Concept)

### What is KOPS?

**KOPS (Kubernetes Operations)** is an Infrastructure-as-Code (IaC) based Kubernetes cluster lifecycle management tool used to create, upgrade, scale, modify, validate, and delete production-grade Kubernetes clusters.

KOPS is most commonly used with **AWS**, but supports multiple infrastructure backends.

Official purpose:

> Create, destroy, upgrade, and maintain production-grade Kubernetes clusters.

### Why was KOPS created?

Before KOPS:

- Kubernetes installation was fully manual.
- Administrators had to configure:
  - Control Plane
  - Worker Nodes
  - ETCD
  - Networking
  - Certificates
  - DNS
  - Load Balancers
- Every upgrade was risky.
- Large organizations running dozens or hundreds of clusters faced operational nightmares.

KOPS automates:

- Cluster Creation
- Cluster Upgrade
- Cluster Modification
- Cluster Deletion
- Rolling Updates
- Auto Scaling Configuration
- HA Cluster Deployment

---

### Real World Analogy

Imagine Amazon has:

- 1 Kubernetes cluster → manageable manually
- 100 Kubernetes clusters → impossible manually

Without KOPS:

You are manually installing operating systems on 100 servers one by one.

With KOPS:

You define a blueprint and KOPS automatically builds, configures and maintains every cluster.

---

### Catastrophic Infrastructure Problems Solved

#### Problem 1: Cluster Drift

Different clusters get configured differently.

Result:

```text
Production cluster works
DR cluster fails
QA cluster behaves differently
```

KOPS makes deployments consistent.

---

#### Problem 2: Upgrade Failures

Manual upgrades often break:

```text
etcd
API Server
Controllers
Worker Nodes
```

KOPS automates rolling upgrades.

---

#### Problem 3: Human Error

Common mistakes:

```text
Wrong certificates
Wrong subnets
Firewall issues
Wrong node sizing
```

KOPS reduces manual activities.

---

## Kubernetes Platforms Used in Production

### Kubernetes

Vanilla Kubernetes deployment.

```text
Full control
Maximum flexibility
More operational overhead
```

---

### OpenShift

Red Hat Kubernetes Distribution.

```text
Enterprise Ready
Integrated Security
Integrated Registry
Integrated CI/CD
```

---

### Tanzu

VMware Kubernetes Platform.

```text
Deep VMware Integration
Enterprise Hybrid Cloud
```

---

### Amazon EKS

AWS Managed Kubernetes.

```text
Control Plane Managed By AWS
Worker Nodes Managed By Customer
```

---

### Azure AKS

Azure Managed Kubernetes.

```text
Control Plane Managed By Azure
Integrated Azure Services
```

---

### Google GKE

Google Managed Kubernetes.

```text
Managed Control Plane
Advanced Autoscaling
```

---

### DKE

Docker Kubernetes Engine.

```text
Docker Managed Kubernetes
```

---

## Cluster Bootstrap Tools

### KOPS

Purpose:

```text
Full Kubernetes Lifecycle Management
```

Capabilities:

- Create
- Upgrade
- Scale
- Validate
- Modify
- Delete

---

### kubeadm

Purpose:

```text
Bootstrap Kubernetes Only
```

Capabilities:

- Initialize control plane
- Join worker nodes

Not designed for:

```text
Infrastructure provisioning
Cluster lifecycle management
```

---

## ⚙️ Architecture & Under the Hood

### KOPS Architecture

```text
+---------------------+
|     User/Admin      |
+---------+-----------+
          |
          v
+---------------------+
|      KOPS CLI       |
+---------+-----------+
          |
          v
+---------------------+
|     S3 State Store  |
+---------+-----------+
          |
          v
+---------------------+
| AWS Infrastructure  |
+---------+-----------+
          |
  ---------------------
  |         |         |
  v         v         v
VPC      Route53   IAM

          |
          v

  ----------------------
  |                    |
  v                    v

Master Nodes      Worker Nodes

          |
          v

       Cluster
```

---

### Core Components

#### 1. KOPS CLI

Used for:

```bash
kops create
kops update
kops validate
kops rolling-update
kops delete
```

Acts as:

```text
Cluster Orchestrator
```

---

#### 2. State Store

Most commonly:

```text
Amazon S3 Bucket
```

Stores:

- Cluster Specs
- Certificates
- Secrets
- Networking Config
- Instance Group Config
- Metadata

Example:

```bash
export KOPS_STATE_STORE=s3://kops-state-storage
```

---

#### 3. Route53

Provides:

```text
Cluster DNS Records
```

Example:

```text
api.k8s-prod.example.com
```

---

#### 4. ETCD

Kubernetes datastore.

Stores:

```text
Pods
Deployments
Services
Secrets
Nodes
Namespaces
```

ETCD runs on control plane nodes.

---

#### 5. Instance Groups

KOPS manages nodes through:

```text
Instance Groups (IG)
```

Similar to:

```text
AWS Auto Scaling Groups
```

Types:

```text
Master Instance Group
Node Instance Group
```

---

### Cluster Creation Workflow

#### Step 1

User executes

```bash
kops create cluster
```

---

#### Step 2

Cluster specification generated.

---

#### Step 3

Saved in State Store.

---

#### Step 4

AWS resources created.

- VPC
- IAM
- ELB
- Subnets
- Security Groups

---

#### Step 5

Control Plane created.

- API Server
- ETCD
- Scheduler
- Controller Manager

---

#### Step 6

Worker Nodes created.

---

#### Step 7

Node registration completed.

---

#### Step 8

Cluster validation completed.

---

## 💻 Essential Execution (Commands & YAML)

# Linux Prerequisites

## Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/stable.txt"

curl -LO \
"https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/amd64/kubectl"

chmod +x kubectl

sudo mv kubectl /usr/local/bin/

kubectl version --client
```

---

## Install AWS CLI

```bash
curl \
"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
-o awscliv2.zip

unzip awscliv2.zip

sudo ./aws/install

aws --version
```

---

## AWS Authentication

```bash
aws configure
```

Required:

```text
Access Key
Secret Key
Region
Output Format
```

---

## Install KOPS

```bash
curl -Lo kops \
https://github.com/kubernetes/kops/releases/latest/download/kops-linux-amd64

chmod +x kops

sudo mv kops /usr/local/bin/

kops version
```

---

# Windows Prerequisites

## Install kubectl

```powershell
curl.exe -LO `
https://dl.k8s.io/release/v1.34.0/bin/windows/amd64/kubectl.exe
```

---

## Verify

```powershell
kubectl version --client
```

---

## Install AWS CLI

Download:

```text
AWSCLIV2.msi
```

Install normally.

---

## Verify

```powershell
aws --version
```

---

## Install KOPS

Download:

```text
kops-windows-amd64.exe
```

Rename:

```text
kops.exe
```

Move into:

```text
C:\Windows\System32
```

Verify:

```powershell
kops version
```

---

# Create State Store

```bash
aws s3api create-bucket \
--bucket my-kops-state-store \
--region us-east-1
```

---

### Configure Environment Variable

```bash
export KOPS_STATE_STORE=s3://my-kops-state-store
```

Verify:

```bash
echo $KOPS_STATE_STORE
```

---

# Create Cluster

```bash
kops create cluster \
--name=prod.k8s.example.com \
--cloud=aws \
--zones=us-east-1a \
--node-count=3 \
--node-size=t3.large \
--control-plane-size=t3.large \
--dns-zone=example.com \
--yes
```

---

### Flag Breakdown

#### --name

```text
Cluster DNS Name
```

Example:

```text
prod.k8s.example.com
```

---

#### --zones

```text
AWS Availability Zone
```

Example:

```text
us-east-1a
```

---

#### --node-count

```text
Worker node count
```

---

#### --node-size

```text
EC2 instance type
```

---

#### --control-plane-size

```text
Master node instance type
```

---

#### --yes

Actually deploy infrastructure.

Without:

```text
Only generates configuration
```

---

# Validate Cluster

```bash
kops validate cluster
```

Expected:

```text
Cluster is ready
```

---

# Export kubeconfig

```bash
kops export kubeconfig \
--name prod.k8s.example.com
```

---

# Verify Access

```bash
kubectl get nodes
```

```bash
kubectl get pods -A
```

---

# Modify Cluster

```bash
kops edit cluster prod.k8s.example.com
```

Example:

```yaml
spec:
  kubernetesVersion: 1.32.0
```

Apply:

```bash
kops update cluster \
--name prod.k8s.example.com \
--yes
```

---

# Instance Groups

List:

```bash
kops get ig
```

Edit:

```bash
kops edit ig nodes-us-east-1a
```

Example:

```yaml
apiVersion: kops.k8s.io/v1alpha2
kind: InstanceGroup

metadata:
  name: nodes-us-east-1a

spec:
  role: Node

  machineType: t3.large

  minSize: 3

  maxSize: 10

  subnets:
    - us-east-1a
```

Apply:

```bash
kops update cluster --yes
```

---

# Upgrade Kubernetes

Check upgrade:

```bash
kops upgrade cluster \
--name prod.k8s.example.com
```

Execute Upgrade:

```bash
kops upgrade cluster \
--name prod.k8s.example.com \
--yes
```

---

# Rolling Update

Required after upgrade.

```bash
kops rolling-update cluster \
--name prod.k8s.example.com \
--yes
```

What happens:

```text
Cordon Node
Drain Node
Upgrade Components
Restart Node
Validate
Move To Next Node
```

---

# Delete Cluster

Dry Run:

```bash
kops delete cluster \
--name prod.k8s.example.com
```

Actual Deletion:

```bash
kops delete cluster \
--name prod.k8s.example.com \
--yes
```

---

# Cluster Specification YAML

```yaml
apiVersion: kops.k8s.io/v1alpha2

kind: Cluster

metadata:
  name: prod.k8s.example.com

spec:

  kubernetesVersion: 1.32.0

  cloudProvider: aws

  networking:
    calico: {}

  api:
    loadBalancer:
      type: Public
```

---

## ⚠️ Production Gotchas & Interview Traps

### Production Failure #1

#### DNS Misconfiguration

Symptoms:

```text
Unable to connect to cluster
kubectl timeout
API unreachable
```

Check:

```bash
nslookup api.prod.k8s.example.com
```

---

### Production Failure #2

#### State Store Deleted

Symptoms:

```text
Cluster exists
KOPS cannot manage it
```

Cause:

```text
S3 bucket removed
```

Impact:

```text
Future upgrades impossible
```

---

### Production Failure #3

#### ETCD Corruption

Symptoms:

```text
API Server unavailable
Pods disappear
```

Check:

```bash
etcdctl endpoint health
```

---

### Production Failure #4

#### Security Group Errors

Symptoms:

```text
Nodes NotReady
Cluster unreachable
```

Check:

```bash
AWS Security Groups
TCP 6443
TCP 10250
TCP 2379
TCP 2380
```

---

## Senior Principal Engineer Interview Questions

### Q1. Difference Between KOPS and kubeadm?

### SRE Answer

```text
kubeadm bootstraps Kubernetes.

KOPS provides complete cluster lifecycle management
including infrastructure creation, upgrades,
rolling updates, scaling and deletion.
```

---

### Q2. Why KOPS Requires State Store?

### SRE Answer

```text
KOPS is declarative.

The state store serves as the source of truth
for certificates, metadata, cluster definition,
instance groups and networking configuration.
```

---

### Q3. Difference Between KOPS and EKS?

### SRE Answer

```text
EKS manages the control plane.

KOPS manages both infrastructure
and Kubernetes components.

KOPS provides deeper control,
EKS reduces operational burden.
```

---

### Q4. How Does KOPS Upgrade a Cluster?

### SRE Answer

```text
KOPS performs rolling updates.

Node is cordoned.
Workloads drained.
Node upgraded.
Health validated.
Traffic restored.

This minimizes downtime.
```

---

### Q5. What AWS Services Are Typically Created By KOPS?

### SRE Answer

```text
VPC
Subnets
Route53
Security Groups
IAM Roles
Load Balancers
Auto Scaling Groups
EC2 Instances
```

---

## 🔍 Debugging (Where to look when it fails)

### Validate Cluster

```bash
kops validate cluster
```

---

### View Cluster

```bash
kops get cluster
```

---

### View Instance Groups

```bash
kops get ig
```

---

### Nodes Status

```bash
kubectl get nodes -o wide
```

---

### Cluster Events

```bash
kubectl get events -A \
--sort-by=.metadata.creationTimestamp
```

---

### Kubelet Logs

```bash
journalctl -u kubelet -f
```

---

### API Server Check

```bash
kubectl get --raw='/readyz'
```

---

### ETCD Health

```bash
etcdctl endpoint health
```

---

### Validate DNS

```bash
nslookup api.prod.k8s.example.com
```

---

### Verify State Store

```bash
aws s3 ls $KOPS_STATE_STORE
```

---

## 📝 10-Second Cheat Sheet

**KOPS (Kubernetes Operations)** is a production-grade Kubernetes lifecycle management tool that provisions and manages complete clusters on AWS using an **S3 State Store** as the source of truth. Unlike **kubeadm**, which only bootstraps Kubernetes, **KOPS manages the entire lifecycle including creation, upgrades, scaling, validation, rolling updates, and deletion of Kubernetes clusters.**


This version is suitable as a complete README.md for GitHub, interview revision, lab practice, and Senior/Principal SRE preparation.
