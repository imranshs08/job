# 🛠️ CKA Troubleshooting Lab 01: Pods & ReplicaSets

Welcome to your first break-and-fix lab! The actual CKA exam will not just ask you to generate YAML—it will present you with broken infrastructure and give you 5 minutes to restore it to working order. 

**Your Mission:**
In this directory, you will find two intentionally corrupted YAML manifests. They contain syntactical, architectural, and logical bugs preventing them from running successfully.

## Objectives
### 1. `broken-pod.yaml`
- Attempt to apply it: `kubectl apply -f broken-pod.yaml` (or just statically analyze the code).
- **Find the 3 distinct errors** in the definition that violate core Kubernetes structural concepts.
- Fix the manifest so a simple Nginx pod boots successfully.

### 2. `broken-replicaset.yaml`
- Analyze the file. This ReplicaSet is failing to maintain the correct number of pods because of a fundamental mismatch in its internal routing.
- **Find the 2 logical errors** that break the controller manager's association with its pods.
- Fix the manifest so it properly scales 3 Nginx replicas.

## How to Submit
Once you've identified the bugs, try to run `kubectl apply --dry-run=client -f <file.yaml>` to see how the Kubernetes API catches the errors!

---

## 🔑 Answer Key & Explanations

### `broken-pod.yaml`
1. **Invalid Image Tag Format**: `image: nginx-1.21.3`
   - *Explanation*: Docker images mandate a colon `:` to separate the repository name from the version tag. Using a hyphen makes Kubernetes assume the tag is missing, and it tries to pull an image literally named "nginx-1.21.3" from dockerhub (which results in `ImagePullBackOff`). The fix is `nginx:1.21.3`.
2. **Invalid YAML Syntax Case**: `restart_policy: Always`
   - *Explanation*: Kubernetes strictly enforces `camelCase` for all API specifications. Snake case (`_`) is invalid. It must be `restartPolicy: Always`. 
3. **Plural Array Requirements**: `port:` (User modification)
   - *Explanation*: Containers can expose multiple ports (e.g., 80, 443). Because it's an array of objects `[ - containerPort: 80 ]`, the key must strictly be pluralized as `ports:`.

### `broken-replicaset.yaml`
1. **Selector and Template Label Mismatch**: 
   - `selector.matchLabels` has `tier: backend`.
   - `template.metadata.labels` has `tier: frontend`.
   - *Explanation*: This is a **fatal logical error**. A ReplicaSet controller uses the `selector` to count how many pods are running. Since the template spins up pods labeled `frontend`, the ReplicaSet will never see them because it is blindly looking for `backend` pods. It will just keep creating infinite pods endlessly until your cluster crashes! The selector labels *must* exactly match the template labels.
