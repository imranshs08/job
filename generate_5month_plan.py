import os

def clean_title(title):
    t = title.split(' - ')[0].replace('|', '-').strip()
    if len(t) > 75:
        return t[:72] + '...'
    return t

with open('titles.txt', 'r', encoding='utf-8') as f:
    titles = [t.strip() for t in f.readlines() if t.strip()]

p1_v = titles[0:53]
p2_v = titles[53:81]
p3_v = titles[81:118]
p4_v = titles[118:148]
p5_v = titles[148:158]

# 1. GENERATE PROGRESS TRACKER
pt_content = """# ✅ Progress Tracker — DevOps Job Switch (5-Month Plan)

> Print this sheet and check off items as you complete them. Review weekly.
> Target Apply Date: Jan 1, 2027

---

## 📺 Complete Video Tracker (158 Videos)

### Phase 1: Foundations & Core DevOps (Aug, Vids 1-53)
| # | Video Title | Watched | Notes | Hands-On |
|---|-------------|---------|-------|----------|
"""
for i, t in enumerate(p1_v):
    pt_content += f"| {i+1} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 2: Cloud Specialization Primary - AWS (Sep, Vids 54-81)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p2_v):
    pt_content += f"| {i+54} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 3: Cloud Secondary & IaC (Oct, Vids 82-118)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p3_v):
    pt_content += f"| {i+82} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 4: Automation - Python & AI (Nov, Vids 119-148)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p4_v):
    pt_content += f"| {i+119} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 5: Observability & Interview Readiness (Dec, Vids 149-158)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p5_v):
    pt_content += f"| {i+149} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += """
---

## 🤖 AI Skills Tracker

| Skill | Started | Practiced | Confident | Used in Project |
|-------|---------|-----------|-----------|-----------------|
| Claude — Basic Prompting | ☐ | ☐ | ☐ | ☐ |
| Claude — DevOps Automation | ☐ | ☐ | ☐ | ☐ |
| Claude — Mock Interviews | ☐ | ☐ | ☐ | ☐ |
| ChatGPT — Code Generation | ☐ | ☐ | ☐ | ☐ |
| ChatGPT — Debugging Assist | ☐ | ☐ | ☐ | ☐ |
| ChatGPT — System Design | ☐ | ☐ | ☐ | ☐ |
| GitHub Copilot — IaC/Code | ☐ | ☐ | ☐ | ☐ |
| GitHub Copilot — Agent Mode | ☐ | ☐ | ☐ | ☐ |
| K8sGPT — Cluster Troubleshoot | ☐ | ☐ | ☐ | ☐ |
| Prompt Engineering for DevOps | ☐ | ☐ | ☐ | ☐ |
"""
with open(r'03-Progress-Tracker\progress-tracker.md', 'w', encoding='utf-8') as f:
    f.write(pt_content)


# 2. GENERATE ROADMAP
rm_content = """# 📍 DevOps Job Switch — 5-Month Master Roadmap

> **Start:** August 1, 2026 → **Finish:** December 31, 2026 → **Apply:** January 1, 2027

---

## 🎯 Phase 1: Foundations & Core DevOps (August)
**Focus:** DevOps Principles, Shell Scripting, Git, Docker, Kubernetes, CI/CD, and Linux fundamentals.

### 📺 Playlist Videos (1 - 53)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p1_v):
    rm_content += f"| {i+1} | {clean_title(t)} |\n"

rm_content += """

---

## ☁️ Phase 2: Cloud Specialization Primary - AWS (September)
**Focus:** AWS Zero to Hero (Networking, Compute, IAM, Security, PaaS).

### 📺 Playlist Videos (54 - 81)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p2_v):
    rm_content += f"| {i+54} | {clean_title(t)} |\n"
    
rm_content += """

---

## 🚀 Phase 3: Cloud Secondary & IaC (October)
**Focus:** Azure Zero to Hero and Terraform.

### 📺 Playlist Videos (82 - 118)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p3_v):
    rm_content += f"| {i+82} | {clean_title(t)} |\n"

rm_content += """
---
## 🐍 Phase 4: Automation - Python & AI (November)
**Focus:** Python for DevOps, AI Assisted DevOps.

### 📺 Playlist Videos (119 - 148)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p4_v):
    rm_content += f"| {i+119} | {clean_title(t)} |\n"

rm_content += """
---
## 🔬 Phase 5: Observability & Interview Readiness (December)
**Focus:** Prometheus, Grafana, OpenSearch, System Design, and Mock Interviews.

### 📺 Playlist Videos (149 - 158)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p5_v):
    rm_content += f"| {i+149} | {clean_title(t)} |\n"


rm_content += """
---
## 🤖 Continuous AI Track (Parallel)
- Set up Claude & ChatGPT accounts for all shell and python learning.
- Use K8sGPT when building out your kubernetes clusters in Phase 1.
- Write Terraform dynamically with GitHub Copilot in Phase 3.
- Use AI explicitly to create study notes on AWS and Azure routing.
"""
with open(r'01-Roadmap\roadmap.md', 'w', encoding='utf-8') as f:
    f.write(rm_content)


# 3. GENERATE WEEKLY PLAN
wp_content = """# 📋 22-Week Study Plan — DevOps Job Switch (5 Months)

> **Duration:** 22 Weeks (Aug 1 - Dec 31)
> **Pace:** ~7.2 Videos/Week (approx 1-2 videos per day)

---
"""
counts = [11, 11, 11, 10, 10, 7, 7, 7, 7, 8, 8, 7, 7, 7, 8, 8, 7, 7, 3, 3, 2, 2]
curr = 0

for w in range(22):
    wp_content += f"\n## 🗓️ WEEK {w+1} — STUDY SCHEDULE\n\n"
    wp_content += "| Iteration | Video Title | Focus/Task |\n"
    wp_content += "|-----------|-------------|------------|\n"
    for _ in range(counts[w]):
        if curr < len(titles):
            wp_content += f"| Vid {curr+1} | {clean_title(titles[curr])} | Watch & Note |\n"
            curr += 1
    wp_content += "\n**Weekly Goal:** Complete listed videos, replicate labs locally, run mock interview questions.\n"
    wp_content += "- [ ] Complete\n"
    wp_content += "---\n"

with open(r'02-Weekly-Plan\weekly-plan.md', 'w', encoding='utf-8') as f:
    f.write(wp_content)


# 4. GENERATE VIDEO TRACKER
vt_content = """# 📺 Complete Video Tracker — 158 Videos

> **Playlist:** Abhishek Veeramalla — DevOps Engineer in 3 Months (2026 Dataset)
> **Total Videos:** 158 | **Schedule:** 22 Weeks (Jul 31 – Dec 31, 2026) @ ~7.2 videos/week

---

## 📊 Overall Progress Dashboard

| Phase | Core Material | Videos | Date Range | Status |
|-------|---------------|--------|---------------|--------|
| **1: Core & Linux** | DevOps 45-day course (pt1) + Linux | 53 | August | ⬜ |
| **2: AWS Primary** | AWS Zero to Hero | 28 | September | ⬜ |
| **3: Azure & IaC** | Azure Zero to Hero + Terraform | 37 | October | ⬜ |
| **4: Automation** | Python & AI DevOps | 30 | November | ⬜ |
| **5: Observability**| Tracing, Logging, Interview Prep | 10 | December | ⬜ |
| **TOTAL** | **The Complete DevOps Engine** | **158** | **22 Weeks** | |

> **Legend:** ⬜ Not Started | 🟨 In Progress | ✅ Complete

---

## 📝 How to Use This Tracker

1. Follow the **[Weekly Plan](../02-Weekly-Plan/weekly-plan.md)** module.
2. Check off files directly in the **[Progress Tracker](../03-Progress-Tracker/progress-tracker.md)** spreadsheet print out.
3. Review progress every Sunday evening.
4. Focus is key. Consistent 1-2 videos a day will let you hit Jan 1 completely ready.
"""
with open(r'08-Video-Tracker\video-tracker.md', 'w', encoding='utf-8') as f:
    f.write(vt_content)

print("SUCCESS: 5-MONTH PLAN REGENERATED!")
