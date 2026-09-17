import re

html_file = 'index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace schedule block with clean classes
old_schedule = r'<div\s+style="display: inline-flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 1rem; width: 100%; box-sizing: border-box; background: rgba\(16, 185, 129, 0\.05\); border: 1px solid rgba\(16, 185, 129, 0\.2\); padding: 0\.6rem 2\.5rem; border-radius: 50px; font-size: 0\.95rem; color: #10b981; font-family: \'JetBrains Mono\', monospace; box-shadow: 0 4px 20px rgba\(16,185,129,0\.1\);">\s*<span>⏱️ Mon-Fri: <strong style="color: #34d399;">2-3 Hrs</strong></span>\s*<span style="opacity: 0\.3;">\|</span>\s*<span>🔥 Sat-Sun: <strong style="color: #34d399;">4-5 Hrs</strong></span>\s*</div>'

new_schedule = """<div class="schedule-pill">
                <span>⏱️ Mon-Fri: <strong style="color: #34d399;">2-3 Hrs</strong></span>
                <span class="separator">|</span>
                <span>🔥 Sat-Sun: <strong style="color: #34d399;">4-5 Hrs</strong></span>
            </div>"""

content = re.sub(old_schedule, new_schedule, content)

# Fix Views/Visitors counter so it can stack on mobile
old_counter = r'<div\s+style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 0\.75rem; text-align: center; background: rgba\(56,189,248,0\.06\); border: 1px solid rgba\(56,189,248,0\.15\); padding: 0\.3rem 1rem; border-radius: 20px; font-family: \'JetBrains Mono\', monospace; font-size: 0\.8rem; color: var\(--text-dim\);">\s*<span>👁️</span>\s*<span>Views: <strong style="color: #38bdf8;" id="busuanzi_value_site_pv">—</strong></span>\s*<span style="opacity:0\.3;">\|</span>\s*<span>Visitors: <strong style="color: #a78bfa;" id="busuanzi_value_site_uv">—</strong></span>\s*</div>'

new_counter = """<div class="views-counter">
                <span>👁️</span>
                <span>Views: <strong style="color: #38bdf8;" id="busuanzi_value_site_pv">—</strong></span>
                <span class="separator">|</span>
                <span>Visitors: <strong style="color: #a78bfa;" id="busuanzi_value_site_uv">—</strong></span>
            </div>"""

content = re.sub(old_counter, new_counter, content)

# Inject classes into the new CSS block
css_to_add = """
        .schedule-pill {
            display: inline-flex; justify-content: center; align-items: center; gap: 1rem;
            background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 0.6rem 2.5rem; border-radius: 50px; font-size: 0.95rem; color: #10b981;
            font-family: 'JetBrains Mono', monospace; box-shadow: 0 4px 20px rgba(16,185,129,0.1);
        }
        .views-counter {
            display: flex; align-items: center; gap: 0.75rem;
            background: rgba(56,189,248,0.06); border: 1px solid rgba(56,189,248,0.15);
            padding: 0.3rem 1rem; border-radius: 20px; font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem; color: var(--text-dim);
        }
        .separator { opacity: 0.3; }

        @media (max-width: 640px) {
            .schedule-pill { flex-direction: column; padding: 1rem 1.5rem; gap: 0.5rem; border-radius: 12px; width: 100%; box-sizing: border-box; }
            .views-counter { flex-direction: column; gap: 0.5rem; padding: 0.8rem; border-radius: 12px; width: 100%; box-sizing: border-box; }
            .separator { display: none; }
            .controls { flex-direction: column; gap: 1rem; padding: 1rem; border-radius: 12px; }
            .btn { width: 100%; }
            .date-display { padding: 0.5rem 0; width: 100%; text-align: center; }
            .countdown-container { gap: 1rem; }
        }
"""
content = content.replace('        @media (max-width: 640px) {', css_to_add + '___MEDIA_MARKER___')
content = content.replace('___MEDIA_MARKER___', '        @media (max-width: 640px) {')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("success!")
