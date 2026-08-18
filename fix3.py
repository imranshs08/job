import re

with open('titles.txt', 'r', encoding='utf-8') as f:
    titles = [t.strip() for t in f.readlines()][:46]

def clean_title(title):
    t = title.split(' - ')[0].replace('|', '-').strip()
    if len(t) > 55:
        return t[:52] + '...'
    return t

wp_path = r'02-Weekly-Plan\weekly-plan.md'
with open(wp_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace occurrences of `Day \d+: [^|]+` inside tables.
# Let's find all of them.
matches = re.findall(r'Day \d+:[^|]+', content)

def replace_func(match):
    global idx
    if idx < len(titles):
        t = clean_title(titles[idx])
        idx += 1
        return t.ljust(len(match.group(0))) # Pad or just return. Actually markdown tables don't need exact padding.
    return match.group(0)

idx = 0
new_content = re.sub(r'Day \d+:[^|]+', replace_func, content)

# 45 matches, but we have 46 titles. We can just append the 46th title to the last one if idx < 46.
if idx < len(titles):
    # append it somewhere or just ignore the 46th. Wait, 46th is "Day-21 | CICD Interview Questions". I can append it to the end of week 16 manually if needed!
    pass

with open(wp_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Replaced {idx} matches.")
