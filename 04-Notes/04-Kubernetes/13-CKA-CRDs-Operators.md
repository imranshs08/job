# CKA Cheat Sheet: CRDs & Operators

> **Scope**: API Extensions  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

Kubernetes is highly extensible. If the native objects (Pods, Deployments, Services) are not enough for your application, you can create your own custom objects using Custom Resource Definitions (CRDs).

---

## 1. Custom Resource Definitions (CRDs)

A CRD acts exactly like a database schema. It tells the Kubernetes API Server: "Hey, I'm inventing a new type of object called a `Backup`. Here is what the YAML for it should look like."

When you define a CRD, you are just defining the structure. Creating a `Backup` object will just store YAML in `etcd`. Nothing will actually *execute* the backup.

**Checking CRDs:**
```bash
# See all custom object definitions in the cluster
kubectl get crd

# See the actual instances of a custom resource (e.g., if you created a CRD named 'Prometheus')
kubectl get prometheus
```

---

## 2. Operators (The Controller)

If a CRD is the *Schema*, the Operator is the *Engine*.

An Operator is a custom controller (usually a Pod running in your cluster, written in Go/Python) that runs a continuous loop. 
1. It watches the API server for changes to your specific Custom Resources.
2. If you apply a YAML file for a custom `Backup` resource, the Operator detects it.
3. The Operator executes code against the real world (e.g., talks to an AWS S3 bucket, dumps the database, and uploads it) to make the desired state a reality!

### 💡 Example: Prometheus Operator
Instead of manually configuring dozens of Prometheus ConfigMaps, you deploy the Prometheus Operator.
You can then write simple YAML files like:
```yaml
kind: ServiceMonitor
metadata:
  name: monitor-my-app
```
Because the `ServiceMonitor` CRD exists, Kubernetes accepts the YAML. The Prometheus Operator pod sees this new `ServiceMonitor`, understands what it means, and automatically reloads the actual Prometheus server configuration.

---

## 3. Exam Notes
CRDs and Operators are advanced topics. For the CKA, you generally do not need to *write* an Operator. However, you must:
1. Know how to check if CRDs exist (`kubectl get crds`).
2. Know how to query custom resources like they are native K8s objects (e.g. `kubectl describe mycustomobject the-object-name`).
3. Understand the conceptual difference between the Definition (CRD) and the Execution logic (Operator).
