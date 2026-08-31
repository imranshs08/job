# 🚢 Helm Cheat Sheet

> **Scope**: Kubernetes Package Management (Beyond CKA)  
> **Note**: Helm is **NOT** part of the Certified Kubernetes Administrator (CKA) exam curriculum. It is covered in CKAD, CKS, and is a vital day-to-day tool for DevOps Engineers, which is why it is in your curriculum.

Helm is the Package Manager for Kubernetes (like `apt` for Ubuntu or `npm` for Node.js). It packages complex Kubernetes applications into manageable "Charts".

---

## 1. Core Architecture

- **Helm Chart**: A bundle of YAML templates and default values (the package itself).
- **Values File (`values.yaml`)**: The configuration file where you input your specific settings (like DB passwords, specific image tags).
- **Release**: A running instance of a Chart in a Kubernetes cluster. You can install the same chart 10 times in a cluster, creating 10 different Releases.

---

## 2. Essential Commands

### 🔍 Searching & Adding Repositories
Helm charts are hosted in repositories (like Bitnami).
```bash
# Add a repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update the local cache (run this before installing to get latest versions)
helm repo update

# Search for a chart
helm search repo bitnami/mysql
```

### 📦 Installing & Upgrading
```bash
# Install a chart (Format: helm install [RELEASE_NAME] [CHART_NAME])
helm install my-db bitnami/mysql

# Install a chart into a specific namespace
helm install my-db bitnami/mysql --namespace production --create-namespace

# Install while overriding the default values.yaml
# (e.g. setting a custom password without needing to edit the raw values file)
helm install my-db bitnami/mysql --set auth.rootPassword=secretpassword1

# Upgrade a running release (e.g., when the underlying chart updates)
helm upgrade my-db bitnami/mysql
```

### 🗑️ Managing Releases
```bash
# List all running Helm releases
helm list -A

# See the history of a release (previous versions)
helm history my-db

# Rollback to a previous release (e.g., to revision 1)
helm rollback my-db 1

# Uninstall / Delete a release completely
helm uninstall my-db
```

---

## 3. Creating Your Own Charts

If you are developing your own microservice, you will need to wrap it in a Helm chart to deploy it cleanly to production.

```bash
# Scaffold a new empty chart
helm create my-webapp
```

This creates a folder structure like this:
```
my-webapp/
  Chart.yaml          # Metadata (Name, version, description)
  values.yaml         # Default configuration values
  charts/             # Sub-charts (Dependencies, e.g., this app needs a DB)
  templates/          # The actual K8s YAML files (but with Go templating logic inside them)
```

**Testing your Chart:**
Before installing your chart, always run a dry-run to ensure the Go templating renders valid Kubernetes YAML.
```bash
helm template my-webapp/
# OR
helm install test-release my-webapp/ --dry-run
```
