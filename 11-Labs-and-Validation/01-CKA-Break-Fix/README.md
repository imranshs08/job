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
Once you've identified the bugs, reply to the chat with:
1. What was broken in the Pod?
2. What was broken in the ReplicaSet?

I will review your fixes and provide Senior-level feedback on your troubleshooting deductions!
