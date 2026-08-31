# CKA Cheat Sheet: RBAC (Roles & Bindings)

> **Scope**: Security & Access Control  
> **Tracker Link**: [kubernetes.md](kubernetes.md)

Role-Based Access Control (RBAC) determines what a user, group, or ServiceAccount can do inside the Kubernetes cluster.

---

## 1. The Core Components

RBAC is broken down into "Who" and "What".

- **Role**: Defines "What" can be done (the permissions: `get, list, watch, create, delete, update`). It is strictly limited to a **specific namespace**.
- **ClusterRole**: Same as a Role, but applies to the **entire cluster** (all namespaces) or for cluster-scoped resources (like Nodes).
- **RoleBinding**: Connects the "Who" (User/Group/ServiceAccount) to a "Role" within a specific namespace.
- **ClusterRoleBinding**: Connects the "Who" to a "ClusterRole" across the entire cluster.

---

## 2. ⚡ Imperative Commands (CKA Speed Strategy)

Writing RBAC YAML from scratch is painfully slow. Use these imperative commands to generate them instantly.

```bash
# 1. Create a ServiceAccount
kubectl create serviceaccount dev-user -n dev-namespace

# 2. Create the Role (e.g., read-only access to pods and logs)
kubectl create role pod-reader --verb=get,list,watch --resource=pods,pods/log -n dev-namespace

# 3. Bind the Role to the ServiceAccount
kubectl create rolebinding dev-user-binding --role=pod-reader --serviceaccount=dev-namespace:dev-user -n dev-namespace

# Create a ClusterRole (has power across all namespaces)
kubectl create clusterrole node-admin --verb=get,list,delete --resource=nodes

# Bind the ClusterRole to a user
kubectl create clusterrolebinding node-admin-binding --clusterrole=node-admin --user=admin-jane
```

---

## 3. Testing Access (Exam Verification)

During the CKA, you MUST verify if your RBAC configuration actually worked. Use the `auth can-i` command!

```bash
# Test as yourself: Can I list pods in the dev namespace?
kubectl auth can-i list pods -n dev-namespace

# Test as the ServiceAccount you just created:
kubectl auth can-i list pods --as=system:serviceaccount:dev-namespace:dev-user -n dev-namespace

# Test a failure case (should return 'no'):
kubectl auth can-i delete pods --as=system:serviceaccount:dev-namespace:dev-user -n dev-namespace
```

---

## 4. Default ClusterRoles to Remember

K8s comes with built-in ClusterRoles you might be asked to bind:
- `cluster-admin`: Superuser access (the literal god mode).
- `admin`: Admin access within a bound namespace.
- `edit`: Can create/edit most resources in a bound namespace, but *cannot* edit Roles or RoleBindings.
- `view`: Read-only access to most objects in a namespace.
