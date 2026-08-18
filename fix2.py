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

# Fix progress-tracker.md
pt_path = r'03-Progress-Tracker\progress-tracker.md'
with open(pt_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith('### Phase 1:'):
        new_lines.append(line)
        new_lines.append("| # | Video Title | Watched | Notes | Hands-On | Revised |\n")
        new_lines.append("|---|-------------|---------|-------|----------|---------|\n")
        for i, t in enumerate(phases[1]):
            new_lines.append(f"| {i+1} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n")
        new_lines.append("\n")
        skip = True
    elif line.startswith('### Phase 2:'):
        new_lines.append(line)
        new_lines.append("| # | Video Title | Watched | Notes | Hands-On | Revised |\n")
        new_lines.append("|---|-------------|---------|-------|----------|---------|\n")
        for i, t in enumerate(phases[2]):
            new_lines.append(f"| {i+15} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n")
        new_lines.append("\n")
        skip = True
    elif line.startswith('### Phase 3:'):
        new_lines.append(line)
        new_lines.append("| # | Video Title | Watched | Notes | Hands-On | Revised |\n")
        new_lines.append("|---|-------------|---------|-------|----------|---------|\n")
        for i, t in enumerate(phases[3]):
            new_lines.append(f"| {i+29} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n")
        new_lines.append("\n")
        skip = True
    elif line.startswith('### Phase 4:'):
        new_lines.append(line)
        new_lines.append("| # | Video Title | Watched | Notes | Hands-On | Revised |\n")
        new_lines.append("|---|-------------|---------|-------|----------|---------|\n")
        for i, t in enumerate(phases[4]):
            new_lines.append(f"| {i+38} | {clean_title(t)} | ☐ | ☐ | ☐ | ☐ |\n")
        new_lines.append("\n")
        skip = True
    elif line.startswith('---') and skip:
        # Reached the end of the tables block
        skip = False
        new_lines.append(line)
    elif line.startswith('## 🤖 AI Skills Tracker') and skip:
        # Just in case
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open(pt_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("progress-tracker updated!")

# Fix roadmap.md
rm_path = r'01-Roadmap\roadmap.md'
with open(rm_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
phase = 0
for line in lines:
    if line.startswith('### 📺 Playlist Videos'):
        phase += 1
        new_lines.append(f"### 📺 Playlist Videos (Phase {phase})\n")
        new_lines.append("| # | Topic / Video Title |\n")
        new_lines.append("|-----|-------|\n")
        
        offset = 0
        if phase == 2: offset = 14
        elif phase == 3: offset = 28
        elif phase == 4: offset = 37
        
        for i, t in enumerate(phases[phase]):
            new_lines.append(f"| {i+1+offset} | {clean_title(t)} |\n")
        new_lines.append("\n")
        skip = True
    elif line.startswith('### 🤖 AI Track'):
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open(rm_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("roadmap updated!")
