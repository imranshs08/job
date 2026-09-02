# 🖥️ Kubernetes Core CLI Concepts (CKA Survival Skills)

> **Scope:** Core tools for navigating the CKA Exam environment without internet access.
> **Path:** `04-Notes/04-Kubernetes/21-CKA-Core-CLI-Commands.md`

During the CKA, you are not allowed to blindly browse Google. You only get the kubernetes.io documentation. However, searching the docs takes too much time. Your best friends are `kubectl explain` and `kubectl api-resources`.

---

## 1. The `kubectl api-resources` Command

This command lists all the resource types that the kubernetes API server understands. 

**Why it's crucial for the CKA:**
If you ever forget what the `kind:` value should be for an object, or what the API version is for a specific resource, THIS command is the answer.

### Common Uses:
```bash
# List every single resource available in the cluster
kubectl api-resources

# Output includes:
# NAME             SHORTNAMES   APIVERSION           NAMESPACED   KIND
# pods             po           v1                   true         Pod
# networkpolicies  netpol       networking.k8s.io/v1 true         NetworkPolicy

# Wait... what is the API group for Deployments?! Check api-resources:
kubectl api-resources | grep -i deployment
# Output: deployments   deploy   apps/v1   true   Deployment
```
**Takeaway:** Never memorize API versions (`apps/v1`, `networking.k8s.io/v1`). Just run `kubectl api-resources`.

---

## 2. The `kubectl explain` Command

This is the ultimate offline dictionary. If you forget how to write a specific line of YAML (e.g., "Where does `tolerations` go inside the Pod spec?"), `kubectl explain` gives you the answer instantly in your terminal.

```bash
# How do I structure a Pod?
kubectl explain pod

# Okay, what goes inside the 'spec' of a Pod?
kubectl explain pod.spec

# How do I define a Liveness Probe?
kubectl explain pod.spec.containers.livenessProbe

# 🚨 THE BEST EXAM TRICK: Use --recursive to see the entire YAML tree at once!
kubectl explain pod --recursive | less
```
**Takeaway:** `explain` gives you the exact YAML nesting structure, meaning you never have to guess indentation levels again.

---

## 3. Imperative vs. Declarative Management

You will use both methods in Kubernetes, but for the CKA Exam, **Imperative is King for speed**.

### Imperative Management (Action-Oriented)
Imperative commands tell Kubernetes *what to do right now, step-by-step*. You manipulate the live cluster directly using CLI commands.

*   **Pros:** EXTREMELY fast. Perfect for exams or rapid debugging.
*   **Cons:** No audit trail. Hard to reproduce in another cluster.

**Examples:**
```bash
# Creating a deployment instantly
kubectl create deployment my-web --image=nginx --replicas=3

# Changing an image instantly
kubectl set image deployment/my-web nginx=nginx:alpine

# Scaling instantly
kubectl scale deployment/my-web --replicas=5
```

### Declarative Management (State-Oriented / GitOps)
Declarative commands tell Kubernetes *the desired final state*. You write a YAML file containing how everything should look, and hand it to the API server. The API server figures out how to get from the current state to that final state.

*   **Pros:** You can put the YAML files in Git (Version Control). Easy peer review (GitOps).
*   **Cons:** Very slow to hand-write YAML from scratch.

**Examples:**
```bash
# Applying a folder full of YAML manifests
kubectl apply -f ./production/

# Applying a single file
kubectl apply -f deployment.yaml
```

---

### 🔥 The Hybrid Exam Strategy (Crucial!)
On the CKA, you MUST combine these two methods. Hand-typing YAML is too slow (Declarative), and single commands can't do complex configurations like mounting Volumes (Imperative).

**The Solution:** Use Imperative commands to generate Declarative YAML templates, then edit the templates!

```bash
# 1. IMPERATIVE STUB GENERATION (--dry-run=client -o yaml)
kubectl run my-pod --image=nginx --dry-run=client -o yaml > pod.yaml

# 2. DECLARATIVE MODIFICATION
vi pod.yaml 
# (Add your volumes, tolerations, or liveness probes inside the text editor)

# 3. DECLARATIVE CREATION
kubectl apply -f pod.yaml
```
