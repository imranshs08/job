# Certified Kubernetes Administrator (CKA) — Readiness Tracker

This document maps the **Official CNCF CKA Syllabus (2026)** against our existing study notes and cheat sheets. It identifies exactly what we have mastered and what gaps remain before the exam.

---

## 1. Troubleshooting (30%)
> Evaluate cluster and node logging, understand monitoring, troubleshoot application failure, cluster component failure, and networking.

- [x] **Application Troubleshooting**: `01-CKA-Pods.md`, `09-CKA-Probes-Resources-HPA.md`
- [x] **Network Troubleshooting**: `11-CKA-NetworkPolicies.md`
- [x] **RESOLVED: Cluster/Node Troubleshooting**: `16-CKA-Troubleshooting.md`

---

## 2. Cluster Architecture, Installation & Configuration (25%)
> Manage RBAC, use Kubeadm to install/upgrade clusters, manage a highly-available ETCD cluster (backup & restore).

- [x] **Role Based Access Control (RBAC)**: `10-CKA-RBAC.md`
- [x] **RESOLVED: Kubeadm & Cluster Upgrades**: `14-CKA-Upgrades.md`
- [x] **RESOLVED: ETCD Backup & Restore**: `15-CKA-ETCD-Backup.md`

---

## 3. Services & Networking (20%)
> Understand host networking, connectivity between pods, ClusterIP, NodePort, LoadBalancer, Ingress controllers, and CoreDNS.

- [x] **Services**: `04-CKA-Services.md`
- [x] **Ingress**: `18-EKS-NGINX-Ingress.md`
- [x] **Network Policies**: `11-CKA-NetworkPolicies.md`
- [x] **RESOLVED: CoreDNS & Manual Networking**: `17-CKA-CoreDNS.md`

---

## 4. Workloads & Scheduling (15%)
> Deployments, DaemonSets, manual scheduling, taints and tolerations, node affinity, and resource scaling.

- [x] **Deployments/ReplicaSets**: `03-CKA-Deployments.md`, `02-CKA-ReplicaSets.md`
- [x] **DaemonSets/StatefulSets**: `08-CKA-StatefulSets-DaemonSets.md`
- [x] **Scaling**: `09-CKA-Probes-Resources-HPA.md`
- [x] **RESOLVED: Advanced Scheduling**: `12-CKA-Scheduling.md`

---

## 5. Storage (10%)
> Understand PVs, PVCs, StorageClasses, emptyDir, hostPath, and configuring applications with persistent storage.

- [x] **Volumes & Persistence**: `07-CKA-Storage.md` *(100% Complete)*

---

## Conclusion
We have achieved **100% curriculum coverage** for the 2026 Certified Kubernetes Administrator (CKA) exam across all 5 official domains!
