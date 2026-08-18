# -*- coding: utf-8 -*-
# Generates a video-by-video tracker for KodeKloud CKA Course
# Data source: KodeKloud course page (pasted by user)
# Start Date: August 18, 2026

from datetime import datetime, timedelta

start_date = datetime(2026, 8, 18)

# NOTE: Scheduling, App Lifecycle, Cluster Maintenance, Security, Storage,
# Networking, kubeadm, Helm, Kustomize, Troubleshooting, Mock Exams
# are collapsed on the public page. Module-level placeholders are added.
# Login to KodeKloud and update these placeholders section by section.

lessons = [
    # === INTRODUCTION ===
    ("Introduction", "Course Introduction / Topics Overview", ""),

    # === CORE CONCEPTS ===
    ("Core Concepts", "Core Concepts Section Introduction", "00:31"),
    ("Core Concepts", "Cluster Architecture", "08:48"),
    ("Core Concepts", "ETCD for Beginners", "07:22"),
    ("Core Concepts", "ETCD in Kubernetes", "03:17"),
    ("Core Concepts", "ETCD – Commands (Optional)", ""),
    ("Core Concepts", "Kube API Server", "04:51"),
    ("Core Concepts", "Kube Controller Manager", "04:15"),
    ("Core Concepts", "Kube Scheduler", "03:53"),
    ("Core Concepts", "Kubelet", "01:42"),
    ("Core Concepts", "Kube Proxy", "03:41"),
    ("Core Concepts", "PODs", "09:13"),
    ("Core Concepts", "PODs with YAML", "07:00"),
    ("Core Concepts", "Demo – PODs with YAML", "06:17"),
    ("Core Concepts", "Practice Test Introduction", "05:45"),
    ("Core Concepts", "Practice Test – PODs", ""),
    ("Core Concepts", "Solution – Pods (optional)", "07:39"),
    ("Core Concepts", "ReplicaSets", "16:09"),
    ("Core Concepts", "Practice Test – ReplicaSets", ""),
    ("Core Concepts", "Solution – ReplicaSets (optional)", "07:46"),
    ("Core Concepts", "Deployments", "04:26"),
    ("Core Concepts", "Certification Tip!", ""),
    ("Core Concepts", "Practice Tests – Deployments", ""),
    ("Core Concepts", "Solution: Deployment (optional)", "05:08"),
    ("Core Concepts", "Services", "13:50"),
    ("Core Concepts", "Services Cluster IP", "04:02"),
    ("Core Concepts", "Services – Loadbalancer", "03:42"),
    ("Core Concepts", "Practice Test Services", ""),
    ("Core Concepts", "Solution: Services (optional)", "05:01"),
    ("Core Concepts", "Namespaces", "08:23"),
    ("Core Concepts", "Practice Test Namespaces", ""),
    ("Core Concepts", "Solution: Namespaces (optional)", "05:03"),
    ("Core Concepts", "Imperative vs Declarative", "13:06"),
    ("Core Concepts", "Certification Tips – Imperative Commands with Kubectl", ""),
    ("Core Concepts", "Practice Test – Imperative Commands", ""),
    ("Core Concepts", "Solution: Imperative Commands (optional)", "07:52"),
    ("Core Concepts", "Kubectl Apply Command", "04:38"),

    # === SCHEDULING (33 topics) ===
    ("Scheduling", "⚠️ EXPAND ON KODEKLOUD – Module has 33 topics (login required)", ""),

    # === LOGGING & MONITORING ===
    ("Logging & Monitoring", "Logging and Monitoring Section Introduction", "00:36"),
    ("Logging & Monitoring", "Monitor Cluster Components", "03:58"),
    ("Logging & Monitoring", "Practice Test Monitor Cluster Components", ""),
    ("Logging & Monitoring", "Solution: Monitor Cluster Components", "03:26"),
    ("Logging & Monitoring", "Managing Application Logs", "02:16"),
    ("Logging & Monitoring", "Practice Test Managing Application Logs", ""),
    ("Logging & Monitoring", "Solution: Logging (Optional)", "02:09"),

    # === APPLICATION LIFECYCLE MANAGEMENT (28 topics) ===
    ("Application Lifecycle", "Application Lifecycle Management – Section Introduction", "00:42"),
    ("Application Lifecycle", "Rolling Updates and Rollbacks", "06:43"),
    ("Application Lifecycle", "Practice Test Rolling Updates and Rollbacks", ""),
    ("Application Lifecycle", "Solution: Rolling update", "09:05"),
    ("Application Lifecycle", "Configure Applications", ""),
    ("Application Lifecycle", "Commands and Arguments in Docker", "07:20"),
    ("Application Lifecycle", "Commands and Arguments in Kubernetes", "02:39"),
    ("Application Lifecycle", "Practice Test Commands and Arguments", ""),
    ("Application Lifecycle", "Solution – Commands and Arguments (Optional)", "10:45"),
    ("Application Lifecycle", "Configure Environment Variables in Applications", "01:15"),
    ("Application Lifecycle", "Configure ConfigMaps in Applications", "05:19"),
    ("Application Lifecycle", "Practice Test Env Variables", ""),
    ("Application Lifecycle", "Solution – Env Variables (Optional)", "09:00"),
    ("Application Lifecycle", "Secrets", "08:20"),
    ("Application Lifecycle", "Practice Test Secrets", ""),
    ("Application Lifecycle", "Additional Resource", ""),
    ("Application Lifecycle", "Solution – Secrets (Optional)", "09:36"),
    ("Application Lifecycle", "Demo: Encrypting Secret Data at Rest", "18:47"),
    ("Application Lifecycle", "A note on Secrets", ""),
    ("Application Lifecycle", "Multi Container Pods", "02:13"),
    ("Application Lifecycle", "Practice Test – Multi Container Pods", ""),
    ("Application Lifecycle", "Solution – Multi Container Pods (Optional)", "15:09"),
    ("Application Lifecycle", "Multi-container Pods Design Patterns", ""),
    ("Application Lifecycle", "Init Containers", ""),
    ("Application Lifecycle", "Practice Test – Init Containers", ""),
    ("Application Lifecycle", "Solution – Init Containers (Optional)", "08:02"),
    ("Application Lifecycle", "Self Healing Applications", ""),
    ("Application Lifecycle", "Download Presentation Deck 4", ""),

    # === CLUSTER MAINTENANCE (19 topics) ===
    ("Cluster Maintenance", "Cluster Maintenance – Section Introduction", "01:16"),
    ("Cluster Maintenance", "OS Upgrades", "03:49"),
    ("Cluster Maintenance", "Practice Test OS Upgrades", ""),
    ("Cluster Maintenance", "Solution – OS Upgrades (optional)", "10:50"),
    ("Cluster Maintenance", "Kubernetes Software Versions", "02:54"),
    ("Cluster Maintenance", "References", ""),
    ("Cluster Maintenance", "Cluster Upgrade Introduction", "11:11"),
    ("Cluster Maintenance", "Demo – Cluster upgrade", "10:49"),
    ("Cluster Maintenance", "Practice Test Cluster Upgrade Process", ""),
    ("Cluster Maintenance", "Solution: Cluster Upgrade Process", "12:36"),
    ("Cluster Maintenance", "Backup and Restore Methods", "06:18"),
    ("Cluster Maintenance", "Working with ETCDCTL", ""),
    ("Cluster Maintenance", "Practice Test Backup and Restore Methods", ""),
    ("Cluster Maintenance", "Solution: Backup and Restore", "18:01"),
    ("Cluster Maintenance", "Practice Test Backup and Restore Methods 2", ""),
    ("Cluster Maintenance", "Solution: Backup and Restore 2", "20:21"),
    ("Cluster Maintenance", "Certification Exam Tip!", ""),
    ("Cluster Maintenance", "References (2)", ""),
    ("Cluster Maintenance", "Download Presentation Deck 5", ""),

    # === SECURITY (45 topics) ===
    ("Security", "Security – Section Introduction", "02:15"),
    ("Security", "Kubernetes Security Primitives", "03:18"),
    ("Security", "Authentication", "05:34"),
    ("Security", "Article on Setting up Basic Authentication", ""),
    ("Security", "TLS Introduction", "01:29"),
    ("Security", "TLS Basics", "20:03"),
    ("Security", "TLS in Kubernetes", "07:48"),
    ("Security", "TLS in Kubernetes – Certificate Creation", "10:55"),
    ("Security", "View Certificate Details", "04:31"),
    ("Security", "Certificate Health Check Spreadsheet", ""),
    ("Security", "Practice Test View Certificate Details", ""),
    ("Security", "Solution – View Certification Details", "21:28"),
    ("Security", "Certificates API", "06:07"),
    ("Security", "Practice Test Certificates API", ""),
    ("Security", "Solution – Certificates API", "07:37"),
    ("Security", "KubeConfig", "08:32"),
    ("Security", "Practice Test KubeConfig", ""),
    ("Security", "Solution – KubeConfig", "08:08"),
    ("Security", "API Groups", "05:52"),
    ("Security", "Authorization", "07:30"),
    ("Security", "Role Based Access Controls", "04:28"),
    ("Security", "Practice Test Role Based Access Controls", ""),
    ("Security", "Solution – Role Based Access Controls", "13:28"),
    ("Security", "Cluster Roles", "04:33"),
    ("Security", "Practice Test Cluster Roles", ""),
    ("Security", "Solution – Cluster Roles", "11:13"),
    ("Security", "Service Accounts", "14:32"),
    ("Security", "Practice Test Service Accounts", ""),
    ("Security", "Solution – Service Accounts", "08:04"),
    ("Security", "Image Security", "04:43"),
    ("Security", "Practice Test Image Security", ""),
    ("Security", "Solution – Image Security", "06:53"),
    ("Security", "Pre-requisite – Security in Docker", "05:37"),
    ("Security", "Security Contexts", "01:52"),
    ("Security", "Practice Test Security Contexts", ""),
    ("Security", "Solution – Security Contexts", "06:12"),
    ("Security", "Network Policies", "08:25"),
    ("Security", "Developing network policies", "11:35"),
    ("Security", "Practice Test Network Policies", ""),
    ("Security", "Solution – Network Policies (optional)", "12:17"),
    ("Security", "Kubectx and Kubens – Command line Utilities", ""),
    ("Security", "Download Presentation Deck 6", ""),
    ("Security", "(2025 Updates) Custom Resource Definition (CRD)", "11:00"),
    ("Security", "(2025 Updates) Custom Controllers", "03:57"),
    ("Security", "⚠️ 1 lesson may be cut off – check KodeKloud Security module", ""),

    # === STORAGE (15 topics) ===
    ("Storage", "Storage – Section Introduction", "00:45"),
    ("Storage", "Introduction to Docker Storage", "00:54"),
    ("Storage", "Storage in Docker", "12:32"),
    ("Storage", "Volume Driver Plugins in Docker", "01:53"),
    ("Storage", "Container Storage Interface", "03:44"),
    ("Storage", "Volumes", "04:30"),
    ("Storage", "Persistent Volumes", "03:01"),
    ("Storage", "Persistent Volume Claims", "04:05"),
    ("Storage", "Using PVC in Pods", ""),
    ("Storage", "Practice Test Persistent Volume Claims", ""),
    ("Storage", "Solution – Persistent Volumes and Persistent Volume Claims (optional)", "18:12"),
    ("Storage", "Storage Class", "03:59"),
    ("Storage", "Practice Test – Storage Class", ""),
    ("Storage", "Solution – Storage Class", "10:28"),
    ("Storage", "Download Presentation Deck 7", ""),

    # === NETWORKING (38 topics) ===
    ("Networking", "Networking Introduction", "02:04"),
    ("Networking", "Prerequisite Switching, Routing, Gateways CNI in kubernetes", "12:12"),
    ("Networking", "Prerequisite DNS", "14:24"),
    ("Networking", "Prerequisite – CoreDNS", ""),
    ("Networking", "Prerequisite Network Namespaces", "15:09"),
    ("Networking", "FAQ", ""),
    ("Networking", "Prerequisite Docker Networking", "07:15"),
    ("Networking", "Prerequisite CNI", "06:10"),
    ("Networking", "Cluster Networking", "02:11"),
    ("Networking", "Important Note about CNI and CKA Exam", ""),
    ("Networking", "Practice Test – Explore Environment", ""),
    ("Networking", "Solution – Explore Environment (optional)", "07:14"),
    ("Networking", "Pod Networking", "09:03"),
    ("Networking", "CNI in kubernetes", "03:06"),
    ("Networking", "Note CNI Weave", ""),
    ("Networking", "CNI weave", "05:59"),
    ("Networking", "Practice Test CNI", ""),
    ("Networking", "Solution – Explore CNI (optional)", "02:12"),
    ("Networking", "Practice Test – Deploy Network Solution", ""),
    ("Networking", "Solution – Deploy Network Solution (optional)", "03:43"),
    ("Networking", "ipam weave", "03:21"),
    ("Networking", "Practice Test – Networking Weave", ""),
    ("Networking", "Solution – Networking Weave (optional)", "05:30"),
    ("Networking", "Service Networking", "08:51"),
    ("Networking", "Practice Test Service Networking", ""),
    ("Networking", "Solution – Service Networking (optional)", "05:12"),
    ("Networking", "DNS in kubernetes", "05:39"),
    ("Networking", "CoreDNS in Kubernetes", "06:44"),
    ("Networking", "Practice Test CoreDNS in Kubernetes", ""),
    ("Networking", "Solution – Explore DNS (optional)", "13:03"),
    ("Networking", "Ingress", "22:34"),
    ("Networking", "Article: Ingress", ""),
    ("Networking", "Ingress – Annotations and rewrite-target", ""),
    ("Networking", "Practice Test – CKA – Ingress Networking – 1", ""),
    ("Networking", "Solution – Ingress Networking – 1 (optional)", "15:46"),
    ("Networking", "Practice Test – CKA – Ingress Networking – 2", ""),
    ("Networking", "Solution – Ingress Networking – 2 (optional)", "10:39"),
    ("Networking", "Download Presentation Deck 8", ""),

    # === DESIGN AND INSTALL (6 topics) ===
    ("Design and Install", "Design a Kubernetes Cluster", "05:50"),
    ("Design and Install", "Choosing Kubernetes Infrastructure", "05:52"),
    ("Design and Install", "Configure High Availability", "07:48"),
    ("Design and Install", "ETCD in HA", "12:42"),
    ("Design and Install", "Important Update: Kubernetes the Hard Way", ""),
    ("Design and Install", "Download Presentation Deck 9", ""),

    # === INSTALL KUBERNETES THE KUBEADM WAY (6 topics) ===
    ("Install kubeadm", "Introduction to Deployment with kubeadm", "02:32"),
    ("Install kubeadm", "Resources", ""),
    ("Install kubeadm", "Deploy with Kubeadm – Provision VMs with Vagrant", "03:06"),
    ("Install kubeadm", "Demo – Deployment with Kubeadm", "14:30"),
    ("Install kubeadm", "Practice Test – Deploy a Kubernetes Cluster using Kubeadm", ""),
    ("Install kubeadm", "Solution – Install a Kubernetes Cluster using kubeadm", "09:50"),

    # === HELM BASICS (11 lessons) ===
    ("Helm Basics", "⚠️ EXPAND ON KODEKLOUD – Module has 11 lessons (login required)", ""),

    # === KUSTOMIZE BASICS (22 lessons) ===
    ("Kustomize Basics", "⚠️ EXPAND ON KODEKLOUD – Module has 22 lessons (login required)", ""),

    # === TROUBLESHOOTING (13 lessons) ===
    ("Troubleshooting", "⚠️ EXPAND ON KODEKLOUD – Module has 13 lessons (login required)", ""),

    # === OTHER TOPICS ===
    ("Other Topics", "Labs – JSON PATH", ""),
    ("Other Topics", "Pre-Requisites – JSON PATH", ""),
    ("Other Topics", "Advanced Kubectl Commands", "12:04"),
    ("Other Topics", "Practice Test – Advanced Kubectl Commands", ""),

    # === LIGHTNING LABS ===
    ("Lightning Labs", "Lightning Lab Introduction", ""),
    ("Lightning Labs", "Lightning Lab – 1", ""),

    # === MOCK EXAMS (10 lessons) ===
    ("Mock Exams", "⚠️ EXPAND ON KODEKLOUD – Module has 10 lessons (login required)", ""),
]

content = """# \u2638\ufe0f KodeKloud CKA \u2014 Video-by-Video Tracker
> **Course:** [Certified Kubernetes Administrator (CKA)](https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator)
> **Instructor:** Mumshad Mannambeth
> **Start Date:** August 18, 2026 | **Target Exam:** October 30, 2026

> \u26a0\ufe0f **Action Required:** Modules marked with \u26a0\ufe0f are collapsed on the public page.
> Login to KodeKloud, click \u201cExpand All\u201d, and paste the lesson names here to complete these rows.

---

| # | Module | Lesson | Duration | Target Date | Done |
|---|--------|---------|----------|-------------|------|
"""

for idx, (module, title, dur) in enumerate(lessons):
    target_day = start_date + timedelta(days=idx)
    target_str = target_day.strftime('%b %d')
    done = "\u2610"
    dash = "\u2014"
    dur_str = dur if dur else dash
    content += f"| {idx+1} | **{module}** | {title} | {dur_str} | {target_str} | {done} |\n"

content += """
---

## \U0001F3af Final Exam Strategy
1. Log into KodeKloud and expand the collapsed sections above \u2014 update this file as you go.
2. After completing all lessons + KodeKloud Mock Exams, move to **killer.sh** (included with exam voucher).
3. Do NOT book your official exam until you score > **90%** on killer.sh.
4. **Target: CKA Exam by October 30, 2026**
"""

with open(r'05-Certifications\kodekloud-cka-tracker.md', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"SUCCESS: CKA tracker generated with {len(lessons)} entries!")
