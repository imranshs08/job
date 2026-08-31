# Certified Kubernetes Administrator (CKA) — Readiness Tracker

This document maps the **Official CNCF CKA Syllabus (2026)** against our existing study notes and cheat sheets. It identifies exactly what we have mastered and what gaps remain before the exam.

---

## 1. Troubleshooting (30%)
> Evaluate cluster and node logging, understand monitoring, troubleshoot application failure, cluster component failure, and networking.

- [x] **Application Troubleshooting**: `CKA-Pods-CheatSheet.md`, `CKA-Probes-Resources-HPA-CheatSheet.md`
- [x] **Network Troubleshooting**: `CKA-NetworkPolicies-CheatSheet.md`
- [x] **RESOLVED: Cluster/Node Troubleshooting**: `CKA-Advanced-Troubleshooting.md`

---

## 2. Cluster Architecture, Installation & Configuration (25%)
> Manage RBAC, use Kubeadm to install/upgrade clusters, manage a highly-available ETCD cluster (backup & restore).

- [x] **Role Based Access Control (RBAC)**: `CKA-RBAC-CheatSheet.md`
- [x] **RESOLVED: Kubeadm & Cluster Upgrades**: `CKA-Kubeadm-Upgrades-CheatSheet.md`
- [x] **RESOLVED: ETCD Backup & Restore**: `CKA-ETCD-Backup-Reset-CheatSheet.md`

---

## 3. Services & Networking (20%)
> Understand host networking, connectivity between pods, ClusterIP, NodePort, LoadBalancer, Ingress controllers, and CoreDNS.

- [x] **Services**: `CKA-Services-CheatSheet.md`
- [x] **Ingress**: `EKS-NGINX-Ingress.md` & `AGIC-to-AGC-Migration.md`
- [x] **Network Policies**: `CKA-NetworkPolicies-CheatSheet.md`
- [x] **RESOLVED: CoreDNS & Manual Networking**: `CKA-CoreDNS-Networking.md`

---

## 4. Workloads & Scheduling (15%)
> Deployments, DaemonSets, manual scheduling, taints and tolerations, node affinity, and resource scaling.

- [x] **Deployments/ReplicaSets**: `CKA-Deployments-CheatSheet.md`, `CKA-ReplicaSets-CheatSheet.md`
- [x] **DaemonSets/StatefulSets**: `CKA-StatefulSets-DaemonSets-CheatSheet.md`
- [x] **Scaling**: `CKA-Probes-Resources-HPA-CheatSheet.md`
- [x] **RESOLVED: Advanced Scheduling**: `CKA-Scheduling-Taints-Affinity.md`

---

## 5. Storage (10%)
> Understand PVs, PVCs, StorageClasses, emptyDir, hostPath, and configuring applications with persistent storage.

- [x] **Volumes & Persistence**: `CKA-Storage-PV-PVC-CheatSheet.md` *(100% Complete)*

---

## Conclusion
We have achieved **100% curriculum coverage** for the 2026 Certified Kubernetes Administrator (CKA) exam across all 5 official domains!
