import os
import json
import re

def clean_title(title):
    import re
    orig_title = title
    for phrase in [
        r'\|?\s*Free DevOps Course.*', 
        r'\|?\s*45 days\s*\|?',
        r'\|?\s*#.*',
        r'-\s*Free DevOps Course.*',
        r'\|?\s*Complete Shell Scripting Playlist.*',
        r'-\s*Complete Shell Scripting Playlist.*',
        r'-\s*#.*',
        r'#\w+'
    ]:
        title = re.sub(phrase, '', title, flags=re.IGNORECASE).strip()
    title = title.replace('|', '-').strip(' -')
    title = re.sub(r'\s+-\s+', ' - ', title)
    title = re.sub(r'-{2,}', '-', title)
    if len(title) > 85:
        return title[:82] + '...'
    return title.strip(' -')

def format_duration(seconds):
    if not seconds:
        return ""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m {s}s"

html_path = r'c:\Job Tracker\DevOps Engineer in 3 Months (DATE)_Export.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

match = re.search(r'const allVideos = (\[.*?\]);', html_content, re.DOTALL)
if not match:
    print("Could not find video data in HTML export.")
    exit(1)

videos = json.loads(match.group(1))

# Keep only the videos we want. The original plan had 158 videos.
videos = videos[:158]

p1_v = videos[0:53]
p2_v = videos[53:81]
p3_v = videos[81:118]
p4_v = videos[118:148]
p5_v = videos[148:158]

# 1. GENERATE PROGRESS TRACKER
pt_content = """# ✅ Progress Tracker — DevOps Job Switch (5-Month Plan)

> Print this sheet and check off items as you complete them. Review weekly.
> Target Apply Date: Jan 1, 2027

---

## 📺 Complete Video Tracker (158 Videos)

### Phase 1: Foundations & Core DevOps (Aug, Vids 1-53)
| # | Video Title | Duration | Watched | Notes | Hands-On |
|---|-------------|----------|---------|-------|----------|
"""
for i, v in enumerate(p1_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    pt_content += f"| {i+1} | [{title}]({url}) | {dur} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 2: Cloud Specialization Primary - AWS (Sep, Vids 54-81)\n"
pt_content += "| # | Video Title | Duration | Watched | Notes | Hands-On |\n|---|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p2_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    pt_content += f"| {i+54} | [{title}]({url}) | {dur} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 3: Cloud Secondary & IaC (Oct, Vids 82-118)\n"
pt_content += "| # | Video Title | Duration | Watched | Notes | Hands-On |\n|---|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p3_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    pt_content += f"| {i+82} | [{title}]({url}) | {dur} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 4: Automation - Python & AI (Nov, Vids 119-148)\n"
pt_content += "| # | Video Title | Duration | Watched | Notes | Hands-On |\n|---|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p4_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    pt_content += f"| {i+119} | [{title}]({url}) | {dur} | ☐ | ☐ | ☐ |\n"

pt_content += "\n### Phase 5: Observability & Interview Readiness (Dec, Vids 149-158)\n"
pt_content += "| # | Video Title | Duration | Watched | Notes | Hands-On |\n|---|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p5_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    pt_content += f"| {i+149} | [{title}]({url}) | {dur} | ☐ | ☐ | ☐ |\n"

with open(r'03-Progress-Tracker\progress-tracker.md', 'w', encoding='utf-8') as f:
    f.write(pt_content)


# 2. GENERATE ROADMAP
rm_content = """# 📍 DevOps Job Switch — 5-Month Master Roadmap

> **Start:** August 1, 2026 → **Finish:** December 31, 2026 → **Apply:** January 1, 2027

---

## 🎯 Phase 1: Foundations & Core DevOps (August)
**Focus:** DevOps Principles, Shell Scripting, Git, Docker, Kubernetes, CI/CD, and Linux fundamentals.

### 📺 Playlist Videos (1 - 53)
| # | Topic / Video Title | Duration |
|-----|-------|----------|
"""
for i, v in enumerate(p1_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    rm_content += f"| {i+1} | [{title}]({url}) | {dur} |\n"

rm_content += """

---

## ☁️ Phase 2: Cloud Specialization Primary - AWS (September)
**Focus:** AWS Zero to Hero (Networking, Compute, IAM, Security, PaaS).

### 📺 Playlist Videos (54 - 81)
| # | Topic / Video Title | Duration |
|-----|-------|----------|
"""
for i, v in enumerate(p2_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    rm_content += f"| {i+54} | [{title}]({url}) | {dur} |\n"
    
rm_content += """

---

## 🚀 Phase 3: Cloud Secondary & IaC (October)
**Focus:** Azure Zero to Hero and Terraform.

### 📺 Playlist Videos (82 - 118)
| # | Topic / Video Title | Duration |
|-----|-------|----------|
"""
for i, v in enumerate(p3_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    rm_content += f"| {i+82} | [{title}]({url}) | {dur} |\n"

rm_content += """
---
## 🐍 Phase 4: Automation - Python & AI (November)
**Focus:** Python for DevOps, AI Assisted DevOps.

### 📺 Playlist Videos (119 - 148)
| # | Topic / Video Title | Duration |
|-----|-------|----------|
"""
for i, v in enumerate(p4_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    rm_content += f"| {i+119} | [{title}]({url}) | {dur} |\n"

rm_content += """
---
## 🔬 Phase 5: Observability & Interview Readiness (December)
**Focus:** Prometheus, Grafana, OpenSearch, System Design, and Mock Interviews.

### 📺 Playlist Videos (149 - 158)
| # | Topic / Video Title | Duration |
|-----|-------|----------|
"""
for i, v in enumerate(p5_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    rm_content += f"| {i+149} | [{title}]({url}) | {dur} |\n"

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
    wp_content += "| Iteration | Video Title | Focus/Task | Est. Duration |\n"
    wp_content += "|-----------|-------------|------------|---------------|\n"
    for _ in range(counts[w]):
        if curr < len(videos):
            v = videos[curr]
            title = clean_title(v.get('Title', ''))
            url = v.get('Video url', '')
            dur = format_duration(v.get('Duration in seconds', 0))
            wp_content += f"| Vid {curr+1} | [{title}]({url}) | Watch & Note | {dur} |\n"
            curr += 1
    wp_content += "\n**Weekly Goal:** Complete listed videos, replicate labs locally, run mock interview questions.\n"
    wp_content += "- [ ] Complete\n"
    wp_content += "---\n"

with open(r'02-Weekly-Plan\weekly-plan.md', 'w', encoding='utf-8') as f:
    f.write(wp_content)

print("SUCCESS: RICH METADATA PLAN REGENERATED!")
