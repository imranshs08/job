import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update terminal-block CSS to ensure no word overflow
content = content.replace(
    'overflow: hidden;',
    'overflow: hidden; word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap;'
)

# 2. Fix inline-flex schedule block (Mon-Fri / Sat-Sun) under header
content = content.replace(
    'display: inline-flex; justify-content: center; align-items: center; gap: 1rem;',
    'display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 1rem; width: 100%; box-sizing: border-box;'
)

# 3. Fix the Views/Visitors counter to allow wrapping
content = content.replace(
    'display: flex; align-items: center; gap: 0.75rem;',
    'display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 0.75rem; text-align: center;'
)

# 4. Remove inline font-size on H1 just to be safe
content = re.sub(r'style="font-size: 3\.5rem; font-weight: 800;(.*?)"', r'style="font-weight: 800;\1"', content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("success!")
