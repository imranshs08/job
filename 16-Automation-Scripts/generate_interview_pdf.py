import subprocess
import sys
import os
import re
import json

MD_PATH = r"c:\Job Tracker\06-Interview-Prep\interview-prep.md"
HTML_PATH = r"c:\Job Tracker\06-Interview-Prep\interview-prep-print.html"
PDF_PATH  = r"c:\Job Tracker\06-Interview-Prep\interview-prep.pdf"

# ── 1. Read markdown ────────────────────────────────────────────────────────
with open(MD_PATH, "r", encoding="utf-8") as f:
    raw_md = f.read()

# ── 2. Convert markdown → HTML using python-markdown ────────────────────────
import markdown as md_lib
html_body = md_lib.markdown(
    raw_md,
    extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
)

# ── 3. Full HTML with premium print CSS ─────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DevOps Interview Preparation Guide</title>
<style>

/* ─── FONTS ──────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ─── PAGE SETUP ────────────────────────────────────────────────────────── */
@page {{
  size: A4;
  margin: 20mm 18mm 20mm 18mm;
}}
@page :first {{
  margin: 0;
}}

/* ─── BASE ──────────────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}

body {{
  font-family: 'Inter', 'Segoe UI', sans-serif;
  font-size: 9.5pt;
  line-height: 1.55;
  color: #1a1a2e;
  background: #fff;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}}

/* ─── COVER PAGE ────────────────────────────────────────────────────────── */
.cover {{
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
  width: 210mm;
  height: 297mm;
  background: linear-gradient(145deg, #0f3460 0%, #16213e 45%, #0f3460 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  page-break-after: always;
  position: relative;
  overflow: hidden;
}}
.cover::before {{
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  top: -100px; left: -100px;
}}
.cover::after {{
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,0.03);
  bottom: -80px; right: -80px;
}}
.cover-inner {{
  z-index: 1;
  text-align: center;
  padding: 0 40px;
}}
.cover-badge {{
  display: inline-block;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.25);
  color: #e0e7ff;
  font-size: 8.5pt;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  padding: 5px 18px;
  border-radius: 50px;
  margin-bottom: 22px;
}}
.cover h1 {{
  font-size: 30pt;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  line-height: 1.1;
  margin-bottom: 16px;
}}
.cover h1 span {{
  color: #60a5fa;
}}
.cover-sub {{
  font-size: 11pt;
  color: #94a3b8;
  margin-bottom: 30px;
}}
.cover-divider {{
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #60a5fa, #818cf8);
  border-radius: 2px;
  margin: 0 auto 28px;
}}
.cover-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 32px;
}}
.cover-tag {{
  background: rgba(96,165,250,0.15);
  border: 1px solid rgba(96,165,250,0.3);
  color: #93c5fd;
  font-size: 7.5pt;
  font-weight: 500;
  padding: 4px 12px;
  border-radius: 20px;
}}
.cover-meta {{
  font-size: 8.5pt;
  color: #64748b;
  margin-top: 10px;
}}
.cover-meta strong {{ color: #94a3b8; }}

/* ─── CONTENT WRAPPER ───────────────────────────────────────────────────── */
.content {{
  padding: 0;
}}

/* ─── HEADINGS ──────────────────────────────────────────────────────────── */
h1 {{
  font-size: 18pt;
  font-weight: 800;
  color: #0f3460;
  border-bottom: 3px solid #0f3460;
  padding-bottom: 6px;
  margin: 0 0 20px 0;
  page-break-after: avoid;
}}
h2 {{
  font-size: 12pt;
  font-weight: 700;
  color: #0f3460;
  background: linear-gradient(90deg, #e8f0fe, transparent);
  border-left: 4px solid #0f3460;
  padding: 7px 12px;
  margin: 22px 0 10px 0;
  border-radius: 0 4px 4px 0;
  page-break-after: avoid;
  break-after: avoid;
}}
h3 {{
  font-size: 10.5pt;
  font-weight: 700;
  color: #1e3a5f;
  margin: 16px 0 8px 0;
  page-break-after: avoid;
}}
h4 {{
  font-size: 9.5pt;
  font-weight: 600;
  color: #334155;
  margin: 12px 0 5px 0;
  page-break-after: avoid;
}}

/* ─── TABLES ─────────────────────────────────────────────────────────────── */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0 16px 0;
  font-size: 8.5pt;
  page-break-inside: auto;
  break-inside: auto;
}}
thead {{
  display: table-header-group;
}}
tr {{
  page-break-inside: avoid;
  break-inside: avoid;
}}
thead tr {{
  background: linear-gradient(135deg, #0f3460, #1e4d8c);
}}
th {{
  color: #ffffff;
  font-weight: 600;
  font-size: 8pt;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  padding: 8px 10px;
  text-align: left;
  border: none;
}}
td {{
  padding: 7px 10px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
  line-height: 1.45;
}}
tbody tr:nth-child(even) td {{
  background: #f8fafc;
}}
tbody tr:hover td {{
  background: #eff6ff;
}}
tbody tr:last-child td {{
  border-bottom: 2px solid #0f3460;
}}
td:first-child {{
  font-weight: 600;
  color: #0f3460;
  white-space: nowrap;
  width: 30px;
}}

/* ─── BLOCKQUOTES ───────────────────────────────────────────────────────── */
blockquote {{
  background: linear-gradient(90deg, #eff6ff, #f8fafc);
  border-left: 4px solid #3b82f6;
  margin: 10px 0;
  padding: 10px 14px;
  border-radius: 0 6px 6px 0;
  font-style: italic;
  color: #334155;
  font-size: 9pt;
  page-break-inside: avoid;
}}
blockquote p {{ margin: 0; }}

/* ─── CODE ──────────────────────────────────────────────────────────────── */
code {{
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 8pt;
  background: #f1f5f9;
  color: #dc2626;
  padding: 1px 5px;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
}}
pre {{
  background: #1e293b;
  color: #e2e8f0;
  padding: 12px 14px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 8pt;
  overflow: hidden;
  margin: 8px 0;
  page-break-inside: avoid;
}}
pre code {{
  background: none;
  color: inherit;
  border: none;
  padding: 0;
}}

/* ─── LISTS ─────────────────────────────────────────────────────────────── */
ul, ol {{
  margin: 5px 0 5px 18px;
  padding: 0;
}}
li {{
  margin-bottom: 3px;
  line-height: 1.5;
}}
li strong {{
  color: #0f3460;
}}

/* ─── HORIZONTAL RULE ───────────────────────────────────────────────────── */
hr {{
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 16px 0;
}}

/* ─── PARAGRAPHS ────────────────────────────────────────────────────────── */
p {{
  margin: 4px 0 8px 0;
}}

/* ─── STRONG ────────────────────────────────────────────────────────────── */
strong {{
  font-weight: 600;
  color: #0f3460;
}}

/* ─── DEEP-DIVE SECTION HIGHLIGHT ───────────────────────────────────────── */
h2:has(+ h3) + h3,
.scenario-highlight {{
  page-break-inside: avoid;
}}

/* ─── PRINT UTILITIES ───────────────────────────────────────────────────── */
@media print {{
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  h2 {{ break-after: avoid; }}
  h3 {{ break-after: avoid; }}
  table {{ break-inside: auto; }}
  tr {{ break-inside: avoid; }}
  thead {{ display: table-header-group; }}
  blockquote {{ break-inside: avoid; }}
  pre {{ break-inside: avoid; }}
}}

</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="cover-inner">
    <div class="cover-badge">🎯 Phase 5 — December 2026</div>
    <h1>DevOps Interview<br><span>Preparation Guide</span></h1>
    <div class="cover-divider"></div>
    <p class="cover-sub">80+ Questions &nbsp;|&nbsp; 12 Sections &nbsp;|&nbsp; Scenario Deep-Dives</p>
    <div class="cover-tags">
      <span class="cover-tag">Linux & Shell</span>
      <span class="cover-tag">Git</span>
      <span class="cover-tag">Docker</span>
      <span class="cover-tag">Kubernetes</span>
      <span class="cover-tag">CI/CD</span>
      <span class="cover-tag">Terraform</span>
      <span class="cover-tag">Cloud (AWS/Azure)</span>
      <span class="cover-tag">Monitoring</span>
      <span class="cover-tag">AI/DevOps</span>
      <span class="cover-tag">Scenarios</span>
      <span class="cover-tag">Behavioral</span>
    </div>
    <p class="cover-meta"><strong>Start Revising:</strong> Week 17 &nbsp;|&nbsp; <strong>Generated:</strong> August 2026</p>
  </div>
</div>

<!-- MAIN CONTENT -->
<div class="content">
{html_body}
</div>

</body>
</html>"""

# ── 4. Write HTML ────────────────────────────────────────────────────────────
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"HTML written: {{HTML_PATH}}")

# ── 5. Find Chrome / Edge ────────────────────────────────────────────────────
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
browser = next((p for p in CHROME_PATHS if os.path.exists(p)), None)
if not browser:
    print("ERROR: Chrome/Edge not found. Install Chrome and retry.")
    sys.exit(1)

print(f"Using browser: {{browser}}")

# ── 6. Print to PDF via headless Chrome ─────────────────────────────────────
cmd = [
    browser,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=5000",
    "--force-color-profile=srgb",
    f"--print-to-pdf={PDF_PATH}",
    "--print-to-pdf-no-header",
    HTML_PATH,
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
if result.returncode == 0 and os.path.exists(PDF_PATH):
    size_kb = os.path.getsize(PDF_PATH) // 1024
    print(f"PDF generated: {{PDF_PATH}} ({{size_kb}} KB)")
else:
    print("Chrome stdout:", result.stdout)
    print("Chrome stderr:", result.stderr)
    sys.exit(1)
