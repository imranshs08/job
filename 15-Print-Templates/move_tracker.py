import re

with open(r'c:\Job Tracker\13-Video-Tracker\video-tracker.md', 'r', encoding='utf-8') as f:
    doc = f.read()

# Using a generic regex so we don't hardcode emojis in python string literals if not strictly needed
# But we can just use the exact text "PARALLEL MODERN DEVOPS SKILLS TRACK"
match = re.search(r'## .*?PARALLEL MODERN DEVOPS SKILLS TRACK.*?---\n', doc, flags=re.DOTALL)
if match:
    block = match.group(0)
    doc = doc.replace(block, '') # remove from bottom
    target = r'## 📖 Phase 1: Foundations'
    doc = doc.replace(target, block + '\n' + target)
    with open(r'c:\Job Tracker\13-Video-Tracker\video-tracker.md', 'w', encoding='utf-8') as f:
        f.write(doc)
    print("MD Successfully moved!")


with open(r'c:\Job Tracker\print\job-tracker.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The HTML block starts at <!-- UDEMY PARALLEL TRACKER --> and ends right before <!-- FINAL PAGE: AI & SCRATCHPAD -->
match_html = re.search(r'    <!-- UDEMY PARALLEL TRACKER -->.*?    <!-- FINAL PAGE: AI & SCRATCHPAD -->', html, flags=re.DOTALL)
if match_html:
    # We want to extract JUST the block without taking the final page comment
    block_matched = match_html.group(0)
    # The block we actually want to move is everything except the last comment
    block = block_matched.replace('    <!-- FINAL PAGE: AI & SCRATCHPAD -->', '')
    
    html = html.replace(block, '') # remove from bottom
    target_html = r'    <!-- PHASE 1 - VIDEOS -->'
    html = html.replace(target_html, block + '\n' + target_html)
    
    with open(r'c:\Job Tracker\print\job-tracker.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML Successfully moved!")
