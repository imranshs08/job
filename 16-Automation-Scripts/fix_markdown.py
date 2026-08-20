import re
import sys

with open('titles.txt', 'r', encoding='utf-8') as f:
    titles = [t.strip() for t in f.readlines()][:46]

phases = {
    1: titles[0:14],
    2: titles[14:28],
    3: titles[28:37],
    4: titles[37:46]
}

def clean_title(title):
    t = title.split(' - ')[0].replace('|', '-').strip()
    if len(t) > 75:
        return t[:72] + '...'
    return t

pt_path = r'03-Progress-Tracker\progress-tracker.md'
with open(pt_path, 'r', encoding='utf-8') as f:
    pt_content = f.read()

p1_md = "### Phase 1: Foundations (Aug 2026)\n| # | Video Title | Watched | Notes | Hands-On | Revised |\n|---|-------------|---------|-------|----------|---------|\n"
for i, t in enumerate(phases[1]):
    p1_md += f"| {i+1} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n"
pt_content = re.sub(r'### Phase 1: Foundations.*?### Phase 2', p1_md + "\n### Phase 2", pt_content, flags=re.DOTALL)

p2_md = "### Phase 2: Containers & Orchestration (Sep 2026)\n| # | Video Title | Watched | Notes | Hands-On | Revised |\n|---|-------------|---------|-------|----------|---------|\n"
for i, t in enumerate(phases[2]):
    p2_md += f"| {i+15} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n"
pt_content = re.sub(r'### Phase 2: Containers.*?### Phase 3', p2_md + "\n### Phase 3", pt_content, flags=re.DOTALL)

p3_md = "### Phase 3: CI/CD & Infrastructure as Code (Oct 2026)\n| # | Video Title | Watched | Notes | Hands-On | Revised |\n|---|-------------|---------|-------|----------|---------|\n"
for i, t in enumerate(phases[3]):
    p3_md += f"| {i+29} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n"
pt_content = re.sub(r'### Phase 3: CI/CD.*?### Phase 4', p3_md + "\n### Phase 4", pt_content, flags=re.DOTALL)

p4_md = "### Phase 4: Cloud, Monitoring & AI/DevOps (Nov 2026)\n| # | Video Title | Watched | Notes | Hands-On | Revised |\n|---|-------------|---------|-------|----------|---------|\n"
for i, t in enumerate(phases[4]):
    p4_md += f"| {i+38} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n"
pt_content = re.sub(r'### Phase 4: Cloud, Monitoring.*?---', p4_md + "\n---", pt_content, flags=re.DOTALL)

with open(pt_path, 'w', encoding='utf-8') as f:
    f.write(pt_content)
print("Updated progress-tracker.md")

rm_path = r'01-Roadmap\roadmap.md'
with open(rm_path, 'r', encoding='utf-8') as f:
    rm_content = f.read()

r1_md = "### 📺 Playlist Videos (Phase 1)\n| # | Topic / Video Title |\n|-----|-------|\n"
for i, t in enumerate(phases[1]):
    r1_md += f"| {i+1} | {clean_title(t)} |\n"
rm_content = re.sub(r'### 📺 Playlist Videos.*?(?=### 🤖 AI Track)', r1_md + "\n", rm_content, count=1, flags=re.DOTALL)

r2_md = "### 📺 Playlist Videos (Phase 2)\n| # | Topic / Video Title |\n|-----|-------|\n"
for i, t in enumerate(phases[2]):
    r2_md += f"| {i+15} | {clean_title(t)} |\n"
rm_content = re.sub(r'### 📺 Playlist Videos.*?(?=### 🤖 AI Track)', r2_md + "\n", rm_content, count=1, flags=re.DOTALL)

r3_md = "### 📺 Playlist Videos (Phase 3)\n| # | Topic / Video Title |\n|-----|-------|\n"
for i, t in enumerate(phases[3]):
    r3_md += f"| {i+29} | {clean_title(t)} |\n"
rm_content = re.sub(r'### 📺 Playlist Videos.*?(?=### 🤖 AI Track)', r3_md + "\n", rm_content, count=1, flags=re.DOTALL)

r4_md = "### 📺 Playlist Videos (Phase 4)\n| # | Topic / Video Title |\n|-----|-------|\n"
for i, t in enumerate(phases[4]):
    r4_md += f"| {i+38} | {clean_title(t)} |\n"
rm_content = re.sub(r'### 📺 Playlist Videos.*?(?=### 🤖 AI Track)', r4_md + "\n", rm_content, count=1, flags=re.DOTALL)

with open(rm_path, 'w', encoding='utf-8') as f:
    f.write(rm_content)

print("Updated roadmap.md")
