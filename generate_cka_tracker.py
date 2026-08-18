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

    # === APPLICATION LIFECYCLE MANAGEMENT (28 lessons) ===
    ("Application Lifecycle", "⚠️ EXPAND ON KODEKLOUD – Module has 28 lessons (login required)", ""),

    # === CLUSTER MAINTENANCE (19 lessons) ===
    ("Cluster Maintenance", "⚠️ EXPAND ON KODEKLOUD – Module has 19 lessons (login required)", ""),

    # === SECURITY (45 lessons) ===
    ("Security", "⚠️ EXPAND ON KODEKLOUD – Module has 45 lessons (login required)", ""),

    # === STORAGE (15 lessons) ===
    ("Storage", "⚠️ EXPAND ON KODEKLOUD – Module has 15 lessons (login required)", ""),

    # === NETWORKING (38 lessons) ===
    ("Networking", "⚠️ EXPAND ON KODEKLOUD – Module has 38 lessons (login required)", ""),

    # === DESIGN AND INSTALL ===
    ("Design and Install", "Design a Kubernetes Cluster", "05:50"),
    ("Design and Install", "Choosing Kubernetes Infrastructure", "05:52"),
    ("Design and Install", "Configure High Availability", "07:48"),
    ("Design and Install", "ETCD in HA", "12:42"),
    ("Design and Install", "Important Update: Kubernetes the Hard Way", ""),

    # === INSTALL KUBERNETES THE KUBEADM WAY (6 lessons) ===
    ("Install kubeadm", "⚠️ EXPAND ON KODEKLOUD – Module has 6 lessons (login required)", ""),

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
