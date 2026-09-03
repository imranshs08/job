# Lab 05: Jenkins Immutable Controller Architecture

## í¾¯ Architecture Objective
Enterprise CI/CD environments cannot tolerate sluggish controller startup sequences, nor can they risk drift when dynamically downloading plugin artifacts at runtime. The standard approach of using `install-plugins.sh` in the container entrypoint causes delays (5-10 minutes) every time Jenkins crashes and reschedules, bottlenecking disaster recovery.

**The Solution:** We will architect an "Immutable Image" where all Jenkins plugins are baked strictly into the Docker filesystem layers utilizing the new `jenkins-plugin-cli` engine during the CI/CD pipeline build phase. 

---

## Step 1: The Component Registry (`plugins.txt`)
Instead of installing plugins manually in the GUI, we define an Enterprise Configuration as Code (JCasC) mapping file representing our absolute baseline.

Create `plugins.txt` on your desktop:
```text
configuration-as-code:1850.va_a_8c31d3158b
git:5.2.2
workflow-aggregator:596.v8c21c963d92d
kubernetes:4213.v0fc2512d93e8
theme-manager:215.vc1ff18d67920
```

---

## Step 2: The Pre-Baked `Dockerfile`
This `Dockerfile` intercepts the boot sequence, overriding the initial wizard and aggressively executing the plugin compilation at build time.

Create `Dockerfile`:
```dockerfile
FROM jenkins/jenkins:lts

# Skip the initial Setup Wizard immediately
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Shift left: copy the dependency list into the build matrix
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt

# Execute the modern plugin CLI during the BUILD phase, NOT runtime!
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
```

---

## Step 3: Local Image Compilation
To test this in our Minikube cluster, we must point our Docker CLI directly to the Minikube daemon, so the image is built perfectly inside the cluster's internal cache without touching Docker Hub.

Run these dynamically in PowerShell:
```bash
# Point your shell to Minikube's Docker Engine
minikube docker-env | Invoke-Expression

# Build the Immutable Image tag
docker build -t my-enterprise-jenkins:1.0 .
```

---

## Step 4: The Sub-10 Second Verification
Because every plugin is natively cached inside the image filesystem, Jenkins bypasses the internet completely.

Deploy it using this `jenkins.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        # Pulling the custom golden image strictly from the local daemon!
        image: my-enterprise-jenkins:1.0
        imagePullPolicy: Never 
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: jenkins-svc
  namespace: default
spec:
  ports:
  - port: 8080
  selector:
    app: jenkins
```

Apply it:
```bash
kubectl apply -f jenkins.yaml
```

*Time the logs! It will hit "Jenkins is fully up and running" in less than 15 seconds!*
