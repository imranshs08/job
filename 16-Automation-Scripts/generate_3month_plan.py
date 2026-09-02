import os

def clean_title(title):
    t = title.split(' - ')[0].replace('|', '-').strip()
    if len(t) > 75:
        return t[:72] + '...'
    return t

with open('titles.txt', 'r', encoding='utf-8') as f:
    titles = [t.strip() for t in f.readlines() if t.strip()]

# Total is 158 videos.
# Phase 1: DevOps Core & Linux (Vids 1-53) (Month 1)
# Phase 2: Cloud Mastery - AWS & Azure (Vids 54-109) (Month 2)
# Phase 3: Terraform, Python, AI, Observability (Vids 110-158) (Month 3)

p1_v = titles[0:53]
p2_v = titles[53:109]
p3_v = titles[109:158]

# 1. GENERATE PROGRESS TRACKER
pt_content = """# ✅ Progress Tracker — DevOps Job Switch (3-Month Intensive)

> Print this sheet and check off items as you complete them. Review weekly.

---

## 📺 Complete Video Tracker (158 Videos)

### Phase 1: DevOps Core & Linux Mastery (Month 1, Vids 1-53)
| # | Video Title | Watched | Notes | Hands-On |
|---|-------------|---------|-------|----------|
"""
for i, t in enumerate(p1_v):
    pt_content += f"| {i+1} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 2: Cloud Mastery - AWS & Azure (Month 2, Vids 54-109)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p2_v):
    pt_content += f"| {i+54} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 3: IaC, Python, AI & Observability (Month 3, Vids 110-158)\n"
pt_content += "| # | Video Title | Watched | Notes | Hands-On |\n|---|-------------|---------|-------|----------|\n"
for i, t in enumerate(p3_v):
    pt_content += f"| {i+110} | {clean_title(t)} | ☐ | ☐ | ☐ |\n"

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
| AI-Enhanced CI/CD | ☐ | ☐ | ☐ | ☐ |
| MLOps Basics | ☐ | ☐ | ☐ | ☐ |
"""
with open(r'03-Progress-Tracker\progress-tracker.md', 'w', encoding='utf-8') as f:
    f.write(pt_content)


# 2. GENERATE ROADMAP
rm_content = """# 📍 DevOps Job Switch — 3-Month Master Roadmap

> **Start:** Imminent → **Finish:** In exactly 3 Months (12 Weeks) → **Goal:** Cloud & AI DevOps Engineer

---

## 🎯 Phase 1: DevOps Core & Linux Mastery (Month 1, Weeks 1-4)
**Focus:** DevOps Principles, Shell Scripting, Git, Docker, Kubernetes, CI/CD, and Linux fundamentals.

### 📺 Playlist Videos (1 - 53)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p1_v):
    rm_content += f"| {i+1} | {clean_title(t)} |\n"

rm_content += """

---

## ☁️ Phase 2: Cloud Mastery - AWS & Azure (Month 2, Weeks 5-8)
**Focus:** AWS Zero to Hero and Azure Zero to Hero (Networking, Compute, IAM, Security, PaaS).

### 📺 Playlist Videos (54 - 109)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p2_v):
    rm_content += f"| {i+54} | {clean_title(t)} |\n"
    
rm_content += """

---

## 🚀 Phase 3: IaC, Python, AI & Observability (Month 3, Weeks 9-12)
**Focus:** Terraform, Python for DevOps, AI Assisted DevOps, Prometheus, Grafana, OpenSearch.

### 📺 Playlist Videos (110 - 158)
| # | Topic / Video Title |
|-----|-------|
"""
for i, t in enumerate(p3_v):
    rm_content += f"| {i+110} | {clean_title(t)} |\n"

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
wp_content = """# 📋 12-Week Study Plan — DevOps Job Switch (3 Months)

> **Duration:** 12 Weeks Intensive
> **Pace:** ~13 Videos/Week (approx 2-3 videos per day)

---
"""

# Let's chunk the 158 videos into 12 weeks mapping to roughly 13 per week.
curr = 0
videos_per_week = [13] * 12
videos_per_week[0] = 14
videos_per_week[11] = 14
# Sum of videos_per_week is 158

for w in range(12):
    wp_content += f"\n## 🗓️ WEEK {w+1} — STUDY SCHEDULE\n\n"
    wp_content += "| Iteration | Video Title | Focus/Task |\n"
    wp_content += "|-----------|-------------|------------|\n"
    count = videos_per_week[w]
    for _ in range(count):
        if curr < len(titles):
            wp_content += f"| Vid {curr+1} | {clean_title(titles[curr])} | Watch & Note |\n"
            curr += 1
    wp_content += "\n**Weekly Goal:** Complete all listed videos, replicate labs locally, and prompt AI for any gaps.\n"
    wp_content += "- [ ] Complete\n"
    wp_content += "---\n"

with open(r'02-Weekly-Plan\weekly-plan.md', 'w', encoding='utf-8') as f:
    f.write(wp_content)


# 4. GENERATE VIDEO TRACKER
vt_content = """# 📺 Complete Video Tracker — 158 Videos

> **Playlist:** Abhishek Veeramalla — DevOps Engineer in 3 Months (2026 Dataset)
> **Total Videos:** 158 | **Schedule:** 12 Weeks (3 Months) @ ~13 videos/week

---

## 📊 Overall Progress Dashboard

| Phase | Core Material | Videos | Est. Duration | Status |
|-------|---------------|--------|---------------|--------|
| **1: Core & Linux** | DevOps 45-day course (pt1) + Linux course | 53 | Weeks 1 - 4 | ⬜ |
| **2: Cloud Mastery** | AWS Zero to Hero + Azure Zero to Hero | 56 | Weeks 5 - 8 | ⬜ |
| **3: Automation & AI** | Terraform, Python, AI, Observability | 49 | Weeks 9 - 12 | ⬜ |
| **TOTAL** | **The Complete DevOps Engine** | **158** | **12 Weeks** | |

> **Legend:** ⬜ Not Started | 🟨 In Progress | ✅ Complete

---

## 📝 How to Use This Tracker

1. Follow the **[Weekly Plan](../02-Weekly-Plan/weekly-plan.md)** module.
2. Check off files directly in the **[Progress Tracker](../03-Progress-Tracker/progress-tracker.md)** spreadsheet print out.
3. Review progress every Sunday evening.
4. If you fall behind, skip the specialized cloud videos (e.g. advanced Azure if you focus on AWS) and revisit later.
"""
with open(r'13-Video-Tracker\video-tracker.md', 'w', encoding='utf-8') as f:
    f.write(vt_content)

print("SUCCESS: 3-MONTH PLAN GENERATED ACCURATELY ACROSS ALL 4 FILES!")
