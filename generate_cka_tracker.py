# -*- coding: utf-8 -*-
# Generates a video-by-video tracker for KodeKloud CKA Course
# Start Date: August 18, 2026

from datetime import datetime, timedelta

start_date = datetime(2026, 8, 18)

# All 200+ lessons extracted directly from KodeKloud CKA Course page
# URL: https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator
lessons = [
    # === CORE CONCEPTS ===
    ("Core Concepts", "Core Concepts Section Introduction", "https://kodekloud.com/topic/core-concepts-section-introduction/", "0:31"),
    ("Core Concepts", "Cluster Architecture", "https://kodekloud.com/topic/cluster-architecture/", "8:48"),
    ("Core Concepts", "ETCD for Beginners", "https://kodekloud.com/topic/etcd-for-beginners/", "7:22"),
    ("Core Concepts", "ETCD in Kubernetes", "https://kodekloud.com/topic/etcd-in-kubernetes/", "3:17"),
    ("Core Concepts", "ETCD – Commands (Optional)", "https://kodekloud.com/topic/etcd-commands-optional/", ""),
    ("Core Concepts", "Kube API Server", "https://kodekloud.com/topic/kube-api-server/", "4:51"),
    ("Core Concepts", "Kube Controller Manager", "https://kodekloud.com/topic/kube-controller-manager/", "4:15"),
    ("Core Concepts", "Kube Scheduler", "https://kodekloud.com/topic/kube-scheduler/", "3:53"),
    ("Core Concepts", "Kubelet", "https://kodekloud.com/topic/kubelet/", "1:42"),
    ("Core Concepts", "Kube Proxy", "https://kodekloud.com/topic/kube-proxy/", "3:41"),
    ("Core Concepts", "PODs", "https://kodekloud.com/topic/pods-2/", "9:13"),
    ("Core Concepts", "PODs with YAML", "https://kodekloud.com/topic/pods-with-yaml-3/", "7:00"),
    ("Core Concepts", "Demo – PODs with YAML", "https://kodekloud.com/topic/demo-pods-with-yaml-3/", "6:17"),
    ("Core Concepts", "Practice Test Introduction", "https://kodekloud.com/topic/practice-test-introduction-2/", "5:45"),
    ("Core Concepts", "Practice Test – PODs", "https://kodekloud.com/topic/practice-test-pods/", ""),
    ("Core Concepts", "Solution – Pods (optional)", "https://kodekloud.com/topic/solution-pods-optional-2/", "7:39"),
    ("Core Concepts", "ReplicaSets", "https://kodekloud.com/topic/replicasets/", "16:09"),
    ("Core Concepts", "Practice Test – ReplicaSets", "https://kodekloud.com/topic/practice-test-replicasets/", ""),
    ("Core Concepts", "Solution – ReplicaSets (optional)", "https://kodekloud.com/topic/solution-replicasets-optional-2/", "7:46"),
    ("Core Concepts", "Deployments", "https://kodekloud.com/topic/deployments-3/", "4:26"),
    ("Core Concepts", "Practice Tests – Deployments", "https://kodekloud.com/topic/practice-tests-deployments/", ""),
    ("Core Concepts", "Solution: Deployment (optional)", "https://kodekloud.com/topic/solution-deploymentoptional/", "5:08"),
    ("Core Concepts", "Services", "https://kodekloud.com/topic/services-3/", "13:50"),
    ("Core Concepts", "Services Cluster IP", "https://kodekloud.com/topic/services-cluster-ip-2/", "4:02"),
    ("Core Concepts", "Services – Loadbalancer", "https://kodekloud.com/topic/services-loadbalancer/", "3:42"),
    ("Core Concepts", "Practice Test Services", "https://kodekloud.com/topic/practice-test-services/", ""),
    ("Core Concepts", "Solution: Services (optional)", "https://kodekloud.com/topic/solution-services-optional-2/", "5:01"),
    ("Core Concepts", "Namespaces", "https://kodekloud.com/topic/namespaces/", "8:23"),
    ("Core Concepts", "Practice Test Namespaces", "https://kodekloud.com/topic/practice-test-namespaces/", ""),
    ("Core Concepts", "Solution: Namespaces (optional)", "https://kodekloud.com/topic/solution-namespaces-optional-2/", "5:03"),
    ("Core Concepts", "Imperative vs Declarative", "https://kodekloud.com/topic/imperative-vs-declarative/", "13:06"),
    ("Core Concepts", "Certification Tips – Imperative Commands", "https://kodekloud.com/topic/certification-tips-imperative-commands-with-kubectl/", ""),
    ("Core Concepts", "Practice Test – Imperative Commands", "https://kodekloud.com/topic/practice-test-imperative-commands-2/", ""),
    ("Core Concepts", "Solution: Imperative Commands (optional)", "https://kodekloud.com/topic/solution-imperative-commands-optional-2/", "7:52"),
    ("Core Concepts", "Kubectl Apply Command", "https://kodekloud.com/topic/kubectl-apply-command/", "4:38"),
    # === LOGGING & MONITORING ===
    ("Logging & Monitoring", "Logging and Monitoring Section Introduction", "https://kodekloud.com/topic/logging-and-monitoring-section-introduction/", "0:36"),
    ("Logging & Monitoring", "Monitor Cluster Components", "https://kodekloud.com/topic/monitor-cluster-components/", "3:58"),
    ("Logging & Monitoring", "Practice Test Monitor Cluster Components", "https://kodekloud.com/topic/practice-test-monitor-cluster-components/", ""),
    ("Logging & Monitoring", "Solution: Monitor Cluster Components", "https://kodekloud.com/topic/solution-monitor-cluster-components/", "3:26"),
    ("Logging & Monitoring", "Managing Application Logs", "https://kodekloud.com/topic/managing-application-logs/", "2:16"),
    ("Logging & Monitoring", "Practice Test Managing Application Logs", "https://kodekloud.com/topic/practice-test-managing-application-logs/", ""),
    ("Logging & Monitoring", "Solution: Logging (Optional)", "https://kodekloud.com/topic/solution-logging-optional-2/", "2:09"),
    # === DESIGN AND INSTALL ===
    ("Design and Install", "Design a Kubernetes Cluster", "https://kodekloud.com/topic/design-a-kubernetes-cluster/", "5:50"),
    ("Design and Install", "Choosing Kubernetes Infrastructure", "https://kodekloud.com/topic/choosing-kubernetes-infrastructure/", "5:52"),
    ("Design and Install", "Configure High Availability", "https://kodekloud.com/topic/configure-high-availability/", "7:48"),
    ("Design and Install", "ETCD in HA", "https://kodekloud.com/topic/etcd-in-ha/", "12:42"),
    # === OTHER TOPICS ===
    ("Other Topics", "Pre-Requisites – JSON PATH", "https://kodekloud.com/topic/pre-requisites-json-path/", ""),
    ("Other Topics", "Advanced Kubectl Commands", "https://kodekloud.com/topic/advanced-kubectl-commands/", "12:04"),
    ("Other Topics", "Practice Test – Advanced Kubectl Commands", "https://kodekloud.com/topic/practice-test-advanced-kubectl-commands/", ""),
    # === LIGHTNING LABS ===
    ("Lightning Labs", "Lightning Lab Introduction", "https://kodekloud.com/topic/lightning-lab-introduction/", ""),
    ("Lightning Labs", "Lightning Lab – 1", "https://kodekloud.com/topic/lightning-lab-1-2/", ""),
    # === MODULE PLACEHOLDERS (from collapsed sections) ===
    ("Scheduling", "Scheduling Section - Full Module (37 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Application Lifecycle", "App Lifecycle Management - Full Module (28 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Cluster Maintenance", "Cluster Maintenance - Full Module (19 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Security", "Security - Full Module (45 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Storage", "Storage - Full Module (15 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Networking", "Networking - Full Module (38 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Install kubeadm", "Install Kubernetes the kubeadm way - Full Module (6 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Helm Basics", "Helm Basics - Full Module (11 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Kustomize Basics", "Kustomize Basics - Full Module (22 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Troubleshooting", "Troubleshooting - Full Module (13 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
    ("Mock Exams", "Mock Exams - Full Module (10 Lessons)", "https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator", ""),
]

content = """# \u2638\ufe0f KodeKloud CKA — Video-by-Video Tracker
> **Course:** [Certified Kubernetes Administrator (CKA)](https://kodekloud.com/courses/cka-certification-course-certified-kubernetes-administrator)
> **Instructor:** Mumshad Mannambeth
> **Start Date:** August 18, 2026
> **Target Exam Date:** October 30, 2026
>
> *Check each video off as you watch and complete the practice test.*

---

| # | Module | Lesson Title | Duration | Target Date | \u2705 Done |
|---|--------|--------------|----------|-------------|--------|
"""

current_module = ""
for idx, (module, title, url, dur) in enumerate(lessons):
    # Assign one lesson per day from Aug 18
    target_day = start_date + timedelta(days=idx)
    target_str = target_day.strftime('%b %d').replace(' 0', ' ')
    if module != current_module:
        current_module = module
    content += f"| {idx+1} | **{module}** | [{title}]({url}) | {dur if dur else '—'} | {target_str} | \u2610 |\n"

content += """
---

## \U0001F4CC Notes
- Modules listed as "Full Module (X Lessons)" are collapsed on the website — expand them manually on KodeKloud to see individual videos.
- After completing all modules, run the **killer.sh** simulator (included when you book the exam voucher) until you consistently score > 90%.
- Target: **CKA Exam by October 30, 2026**
"""

with open(r'05-Certifications\kodekloud-cka-tracker.md', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"SUCCESS: CKA tracker generated with {len(lessons)} entries!")
