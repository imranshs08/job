# -*- coding: utf-8 -*-
import os
import json
import re
from datetime import datetime, timedelta

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

videos = json.loads(match.group(1))[:158]

start_date = datetime(2026, 8, 1)
def get_target_date(idx):
    day_offset = int(idx * 153 / 158)
    d = start_date + timedelta(days=day_offset)
    return d.strftime('%b %d').replace(' 0', ' ')

def get_status(idx):
    if idx < 9:
        return '\u2705' # check mark
    return '\u2610' # empty ballot box

p1_v = videos[0:53]
p2_v = videos[53:81]
p3_v = videos[81:118]
p4_v = videos[118:148]
p5_v = videos[148:158]

# 1. GENERATE PROGRESS TRACKER
pt_content = f"""# \u2705 Progress Tracker — DevOps Job Switch (5-Month Plan)

> Print this sheet and check off items as you complete them. Review weekly.
> Target Apply Date: Jan 1, 2027

---

## \U0001F4FA Complete Video Tracker (158 Videos)

### Phase 1: Foundations & Core DevOps (Aug, Vids 1-53)
| # | Video Title | Target Date | Duration | Watched | Notes | Hands-On |
|---|-------------|-------------|----------|---------|-------|----------|
"""
for idx, v in enumerate(p1_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    status = get_status(idx)
    pt_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} | {status} | {status} | {status} |\n"

pt_content += "\n### Phase 2: Cloud Specialization Primary - AWS (Sep, Vids 54-81)\n"
pt_content += "| # | Video Title | Target Date | Duration | Watched | Notes | Hands-On |\n|---|-------------|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p2_v):
    idx = i + 53
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    status = get_status(idx)
    pt_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} | {status} | {status} | {status} |\n"

pt_content += "\n### Phase 3: Cloud Secondary & IaC (Oct, Vids 82-118)\n"
pt_content += "| # | Video Title | Target Date | Duration | Watched | Notes | Hands-On |\n|---|-------------|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p3_v):
    idx = i + 81
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    status = get_status(idx)
    pt_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} | {status} | {status} | {status} |\n"

pt_content += "\n### Phase 4: Automation - Python & AI (Nov, Vids 119-148)\n"
pt_content += "| # | Video Title | Target Date | Duration | Watched | Notes | Hands-On |\n|---|-------------|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p4_v):
    idx = i + 118
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    status = get_status(idx)
    pt_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} | {status} | {status} | {status} |\n"

pt_content += "\n### Phase 5: Observability & Interview Readiness (Dec, Vids 149-158)\n"
pt_content += "| # | Video Title | Target Date | Duration | Watched | Notes | Hands-On |\n|---|-------------|-------------|----------|---------|-------|----------|\n"
for i, v in enumerate(p5_v):
    idx = i + 148
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    status = get_status(idx)
    pt_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} | {status} | {status} | {status} |\n"

with open(r'03-Progress-Tracker\progress-tracker.md', 'w', encoding='utf-8') as f:
    f.write(pt_content)


# 2. GENERATE ROADMAP
rm_content = """# \U0001F4CD DevOps Job Switch — 5-Month Master Roadmap

> **Start:** August 1, 2026 → **Finish:** December 31, 2026 → **Apply:** January 1, 2027

---

## \U0001F3AF Phase 1: Foundations & Core DevOps (August)
**Focus:** DevOps Principles, Shell Scripting, Git, Docker, Kubernetes, CI/CD, and Linux fundamentals.

### \U0001F4FA Playlist Videos (1 - 53)
| # | Topic / Video Title | Target Date | Duration |
|-----|-------|-------------|----------|
"""
for idx, v in enumerate(p1_v):
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    rm_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} |\n"

rm_content += """

---

## \u2601\uFE0F Phase 2: Cloud Specialization Primary - AWS (September)
**Focus:** AWS Zero to Hero (Networking, Compute, IAM, Security, PaaS).

### \U0001F4FA Playlist Videos (54 - 81)
| # | Topic / Video Title | Target Date | Duration |
|-----|-------|-------------|----------|
"""
for i, v in enumerate(p2_v):
    idx = i + 53
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    rm_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} |\n"
    
rm_content += """

---

## \U0001F680 Phase 3: Cloud Secondary & IaC (October)
**Focus:** Azure Zero to Hero and Terraform.

### \U0001F4FA Playlist Videos (82 - 118)
| # | Topic / Video Title | Target Date | Duration |
|-----|-------|-------------|----------|
"""
for i, v in enumerate(p3_v):
    idx = i + 81
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    rm_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} |\n"

rm_content += """
---
## \U0001F40D Phase 4: Automation - Python & AI (November)
**Focus:** Python for DevOps, AI Assisted DevOps.

### \U0001F4FA Playlist Videos (119 - 148)
| # | Topic / Video Title | Target Date | Duration |
|-----|-------|-------------|----------|
"""
for i, v in enumerate(p4_v):
    idx = i + 118
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    rm_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} |\n"

rm_content += """
---
## \U0001F52C Phase 5: Observability & Interview Readiness (December)
**Focus:** Prometheus, Grafana, OpenSearch, System Design, and Mock Interviews.

### \U0001F4FA Playlist Videos (149 - 158)
| # | Topic / Video Title | Target Date | Duration |
|-----|-------|-------------|----------|
"""
for i, v in enumerate(p5_v):
    idx = i + 148
    title = clean_title(v.get('Title', ''))
    url = v.get('Video url', '')
    dur = format_duration(v.get('Duration in seconds', 0))
    t_date = get_target_date(idx)
    rm_content += f"| {idx+1} | [{title}]({url}) | {t_date} | {dur} |\n"

with open(r'01-Roadmap\roadmap.md', 'w', encoding='utf-8') as f:
    f.write(rm_content)

# 3. GENERATE WEEKLY PLAN
wp_content = """# \U0001F4CB 22-Week Study Plan — DevOps Job Switch (5 Months)

> **Duration:** 22 Weeks (Aug 1 - Dec 31)
> **Pace:** ~7.2 Videos/Week (approx 1-2 videos per day)

---
"""
counts = [11, 11, 11, 10, 10, 7, 7, 7, 7, 8, 8, 7, 7, 7, 8, 8, 7, 7, 3, 3, 2, 2]
curr = 0

for w in range(22):
    wp_content += f"\n## \U0001F5D3\uFE0F WEEK {w+1} — STUDY SCHEDULE\n\n"
    wp_content += "| Iteration | Video Title | Target Date | Est. Duration |\n"
    wp_content += "|-----------|-------------|-------------|---------------|\n"
    for _ in range(counts[w]):
        if curr < len(videos):
            v = videos[curr]
            title = clean_title(v.get('Title', ''))
            url = v.get('Video url', '')
            dur = format_duration(v.get('Duration in seconds', 0))
            t_date = get_target_date(curr)
            
            checked_mark = "\u2705" if curr < 9 else "Watch & Note"
            wp_content += f"| Vid {curr+1} | [{title}]({url}) | {t_date} | {dur} |\n"
            curr += 1
    wp_content += "\n**Weekly Goal:** Complete listed videos, replicate labs locally, run mock interview questions.\n"
    wp_content += "- [ ] Complete\n"
    wp_content += "---\n"

with open(r'02-Weekly-Plan\weekly-plan.md', 'w', encoding='utf-8') as f:
    f.write(wp_content)

print("SUCCESS: RICH METADATA PLAN REGENERATED!")
