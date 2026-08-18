import os
import json
import re

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Job Switch 2027 — Master Workbook</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            margin: 0; 
            padding: 0;
            background: #e9ecef;
            color: #111;
        }
        
        .page {
            background: white;
            width: 210mm;
            min-height: 297mm;
            margin: 20px auto;
            padding: 20mm;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
        }

        @media print {
            body { background: white; margin: 0; padding: 0; }
            .page { 
                margin: 0; 
                padding: 15mm; 
                width: 100%; 
                min-height: 100vh;
                box-shadow: none;
                page-break-after: always;
            }
            .no-print { display: none !important; }
        }

        /* Typography */
        h1 { font-size: 2.2rem; font-weight: 900; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 5px; color: #0a0a1a; }
        h2 { font-size: 1.4rem; font-weight: 800; border-bottom: 2px solid #000; padding-bottom: 5px; margin-top: 0; text-transform: uppercase; color: #1a1a2e; }
        h3 { font-size: 1.1rem; font-weight: 700; margin: 15px 0 10px 0; color: #333; }
        p { font-size: 0.9rem; margin-bottom: 10px; color: #444; }

        /* Cover Specifics */
        .cover-header { border-bottom: 4px solid #000; padding-bottom: 10px; margin-bottom: 30px; }
        .subtitle { font-size: 1.1rem; font-weight: 600; color: #555; text-transform: uppercase; }
        .metadata-box { border: 2px solid #000; padding: 20px; margin-bottom: 20px; font-weight: 600; font-size: 1rem; }
        .metadata-line { margin: 15px 0; border-bottom: 1px dashed #000; padding-bottom: 2px; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.85rem; }
        th, td { border: 1px solid #aaa; padding: 8px; text-align: left; }
        th { background: #f4f4f4; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; }
        td.check-col { width: 40px; text-align: center; }
        input[type="checkbox"] { width: 14px; height: 14px; border: 1px solid #000; }

        /* Matrices & Checkboxes */
        .check-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem; }
        .check-item { display: flex; align-items: center; gap: 8px; }

        /* Badges */
        .badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; border: 1px solid #000; }

        /* Notebook Paper Formatting */
        .ruled-page {
            background-image: repeating-linear-gradient(transparent, transparent 31px, #ccc 31px, #ccc 32px);
            min-height: 200mm;
            width: 100%;
            margin-top: 20px;
        }
        .sketch-box {
            border: 2px dashed #888;
            height: 200mm;
            width: 100%;
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #aaa;
            font-weight: 600;
        }

        /* Footer */
        .page-footer {
            position: absolute;
            bottom: 15mm;
            left: 20mm;
            right: 20mm;
            font-size: 0.7rem;
            color: #666;
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #ccc;
            padding-top: 5px;
        }
    </style>
</head>
<body>

    <!-- PAGE 1: COVER -->
    <div class="page">
        <div class="cover-header">
            <h1>DEVOPS JOB SWITCH 2027</h1>
            <div class="subtitle">ENTERPRISE MASTER WORKBOOK & ARCHITECTURE GUIDE</div>
            <p style="margin-top:10px; font-size:0.85rem; color:#666;">A4 PRINT EDITION — 158-VIDEO IMMERSIVE ROADMAP</p>
        </div>

        <h3>📋 WORKBOOK OWNERSHIP & PROJECT METADATA</h3>
        <div class="metadata-box">
            <div class="metadata-line">Lead Engineer / Owner: ____________________________________________________________________</div>
            <div class="metadata-line">Target Role & Level: ___________________________________ Expected CTC: ______________________</div>
            <div class="metadata-line">Workbook Start Date: _____ / _____ / 2026      Target Apply Date: 01 / 01 / 2027</div>
            <div class="metadata-line">Primary Cloud Stack: [ ] AWS    [ ] Azure    [ ] GCP    Primary IaC: [ ] Terraform    [ ] Bicep</div>
        </div>

        <h3>🎯 ARCHITECTURE TOPOLOGY OVERVIEW & CORE OBJECTIVES</h3>
        <p>This master guide is designed to transform you into an enterprise-grade DevOps Engineer over the span of 5 months. Following the "DevOps Zero to Hero" blueprint, this workbook establishes the physical trail of your digital learning.</p>
        <p><strong>1. Global Deployment Confidence:</strong> Automating deployments via CI/CD, Containerization, and AWS/Azure.</p>
        <p><strong>2. Operational Observability:</strong> Mastering K8s monitoring, ELK stack, and Prometheus.</p>
        <p><strong>3. Zero-Trust IaC:</strong> Enforcing security natively via Terraform, Ansible, and DevSecOps.</p>

        <h3>⚡ QUICK-START INSTRUCTIONS FOR PRINT & STUDY</h3>
        <p><strong>1. WATCH & TICK:</strong> As you watch each video (1 to 158), tick the checkbox in the phase tables.</p>
        <p><strong>2. USE RULED PAGES:</strong> Turn to the dedicated 8mm notebook sheets following each phase video list to draft notes, CLI commands, and concepts.</p>
        <p><strong>3. SKETCH ARCHITECTURES:</strong> Use the sketch-box pages to draw VPC setups, K8s networking, and Jenkins CI/CD flow diagrams by hand.</p>

        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Cover Page</span>
        </div>
    </div>

    <!-- PAGE 2: MASTER DASHBOARD -->
    <div class="page">
        <h2>MASTER LEARNING PROGRESS TRACKER</h2>
        <p>Tick off each milestone as you progress through video modules, notes, and lab deployments.</p>
        
        <h3>📊 END-TO-END IMPLEMENTATION PROGRESS CHECKLIST</h3>
        <table>
            <tr>
                <th>Phase Title</th>
                <th class="check-col">Video</th>
                <th class="check-col">Notes</th>
                <th class="check-col">Lab</th>
                <th class="check-col">Tested</th>
                <th class="check-col">Mastery</th>
            </tr>
            <tr>
                <td>Phase 1: Foundations (Linux, Shell, Git, AWS)</td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td>Phase 2: Containers & Orchestration (Docker, K8s)</td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td>Phase 3: CI/CD & IaC (Jenkins, Terraform, Ansible)</td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td>Phase 4: Advanced (Monitoring, Python, DevSecOps)</td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td>Phase 5: AI, Capstone & Career Readiness</td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
        </table>

        <h3>⏱️ STUDY & LAB HOURS LOG BOOK</h3>
        <table>
            <tr><th>Date</th><th>Phase / Topic</th><th>Hours</th><th>Sign-Off</th></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
            <tr><td>__/__/26</td><td>___________________________________</td><td>___ hrs</td><td>________</td></tr>
        </table>
        
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Master Dashboard</span>
        </div>
    </div>

{PHASES_HTML}

    <!-- PARALLEL AI TACK PAGE -->
    <div class="page">
        <h2>PARALLEL TRACK: AI-AUGMENTED DEVOPS</h2>
        <p><strong>Focus:</strong> Becoming a Next-Gen 10x DevOps Engineer alongside your standard syllabus. (Starts Aug 1st)</p>

        <h3>REQUIRED AI SKILLS FOR DEVOPS (2026/2027)</h3>
        <table style="margin-bottom: 25px;">
            <tr><th>Skill Area</th><th>Use Case in DevOps</th><th>Mastery</th></tr>
            <tr>
                <td><strong>1. Generative LLM for IaC</strong></td>
                <td>Using Claude 3.5 / ChatGPT to write complex Terraform, Ansible playbooks, and K8s YAML instantly.</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>2. AI Troubleshooting (K8sGPT)</strong></td>
                <td>Piping cluster logs (CrashLoopBackOffs, OOMKILLED) into AI to auto-diagnose root causes in seconds.</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>3. AI Coding Assistants</strong></td>
                <td>Using GitHub Copilot inside VS Code to auto-complete CI/CD pipeline scripts (Jenkinsfiles/GitLab CI).</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>4. Agentic Workflows</strong></td>
                <td>Building lightweight AI agents (Python/LangChain) to automate repetitive JIRA ticket resolution or user provisioning.</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
        </table>

        <h3>AI COURSE RECOMMENDED TRACKER</h3>
        <table>
            <tr><th>Month</th><th>Recommended Course / Resource</th><th>Target</th><th>Done</th></tr>
            <tr>
                <td><strong>Aug</strong> (Foundations)</td>
                <td><strong>Udemy:</strong> AI Prompt Engineering for IT Pros (ChatGPT, Claude)<br><em>Apply it to Shell Scripting & Linux commands.</em></td>
                <td>Aug 30</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>Sep</strong> (Kubernetes)</td>
                <td><strong>YouTube/Free:</strong> K8sGPT & AI Troubleshooting Tutorials<br><em>Use AI to debug your broken Pods and Deployments.</em></td>
                <td>Sep 30</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>Oct</strong> (CI/CD & IaC)</td>
                <td><strong>Udemy:</strong> Mastering GitHub Copilot for DevOps Engineers<br><em>Generate Terraform modules and Jenkinsfiles with AI.</em></td>
                <td>Oct 30</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>Nov</strong> (Cloud)</td>
                <td><strong>Udemy:</strong> Mastering GenAI for DevSecOps & AIOps<br><em>Use LLMs for security scanning, AWS boto3 automation.</em></td>
                <td>Nov 30</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
            <tr>
                <td><strong>Dec</strong> (Interview)</td>
                <td><strong>Project:</strong> Build your own DevOps terminal AI assistant (Python).<br><em>Showcase this on your resume!</em></td>
                <td>Dec 15</td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>
        </table>

        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Parallel AI Track</span>
        </div>
    </div>

    <!-- FINAL PAGE: AI & SCRATCHPAD -->
    <div class="page">
        <h2>WORKBOOK SHEET — AI PROMPT ENGINEERING LOG</h2>
        <p>Record your best ChatGPT/Claude prompts and AI optimization strategies.</p>
        <div class="ruled-page" style="min-height: 240mm;"></div>
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>AI Prompt Log</span>
        </div>
    </div>

</body>
</html>
"""

def clean_title(title):
    t = title.split(' - ')[0].replace('|', '-').strip()
    if len(t) > 75:
        return t[:72] + '...'
    return t

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
    html_src = f.read()

match = re.search(r'const allVideos = (\[.*?\]);', html_src, re.DOTALL)
if match:
    videos = json.loads(match.group(1))[:158]
else:
    print("Could not find video data")
    exit(1)

def extract_videos(start, end, vids):
    res = []
    for i, v in enumerate(vids[start:end]):
        num = start + i + 1
        t = clean_title(v.get('Title', ''))
        d = format_duration(v.get('Duration in seconds', 0))
        url = v.get('Video url', '')
        res.append((num, t, d, url))
    return res

phases = {
    1: {
        "title": "PHASE 1: FOUNDATIONS (AUG 1 – SEP 4)",
        "subtitle": "DevOps Intro, Linux, Shell Scripting, Git, & AWS Basics",
        "videos": extract_videos(0, 53, videos)
    },
    2: {
        "title": "PHASE 2: CONTAINERS & K8S (SEP 5 – OCT 19)",
        "subtitle": "Docker, Kubernetes Architecture, Helm, and AKS/EKS",
        "videos": extract_videos(53, 81, videos)
    },
    3: {
        "title": "PHASE 3: CI/CD & IaC (OCT 20 – NOV 23)",
        "subtitle": "Jenkins CI/CD, Terraform Provisioning, Ansible Configuration Mgmt",
        "videos": extract_videos(81, 118, videos)
    },
    4: {
        "title": "PHASE 4: ADVANCED TOPICS (NOV 24 – DEC 23)",
        "subtitle": "Monitoring, Python for DevOps, DevSecOps, & GitOps / ArgoCD",
        "videos": extract_videos(118, 148, videos)
    },
    5: {
        "title": "PHASE 5: AI, CAPSTONE & CAREER (DEC 24 – 31)",
        "subtitle": "AI Prompts, AI Agents, Interview Preps & Capstone Build",
        "videos": extract_videos(148, 158, videos)
    }
}

phases_html = ""

for p, data in phases.items():
    # Page A: The Video List
    phases_html += f"""
    <!-- PHASE {p} - VIDEOS -->
    <div class="page">
        <h2>{data['title']}</h2>
        <p><strong>Focus:</strong> {data['subtitle']}</p>
        
        <table>
            <tr><th>Video #</th><th>Topic Title</th><th>Dur.</th><th>URL</th><th>Done</th></tr>"""
            
    for v in data['videos']:
        phases_html += f"""
            <tr>
                <td>#{v[0]}</td>
                <td>{v[1]}</td>
                <td>{v[2]}</td>
                <td><a href="{v[3]}" target="_blank" style="color:#0a66c2;text-decoration:none;">Watch Target</a></td>
                <td class="check-col"><input type="checkbox"></td>
            </tr>"""
            
    phases_html += f"""
        </table>
        
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Phase {p} Tracker</span>
        </div>
    </div>
    """
    
    # Page B: Ruled Sheet for Takesaways
    phases_html += f"""
    <!-- PHASE {p} - TAKEAWEAYS -->
    <div class="page">
        <h2>PHASE {p} WORKBOOK — KEY TAKEAWAYS</h2>
        <p>Date Studied: ______________ &nbsp;&nbsp;&nbsp; Mastery Level: [ ] Entry [ ] Competent [ ] Master</p>
        <p style="color:#777; font-size:0.8rem">Use the lined area below for notes during your video study.</p>
        <div class="ruled-page"></div>
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Phase {p} Sheet 1</span>
        </div>
    </div>
    """

    # Page C: Params & Commands
    phases_html += f"""
    <!-- PHASE {p} - COMMANDS -->
    <div class="page">
        <h2>PHASE {p} WORKBOOK — CONFIG SPECS & COMMANDS</h2>
        <p>Record core CLI commands, configurations, and Terraform block blueprints.</p>
        <div class="ruled-page"></div>
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Phase {p} Sheet 2</span>
        </div>
    </div>
    """
    
    # Page D: Sketchpad
    phases_html += f"""
    <!-- PHASE {p} - SKETCHPAD -->
    <div class="page">
        <h2>PHASE {p} WORKBOOK — FLOW CANVAS</h2>
        <p>Verification Check: [ ] Completed Lab</p>
        <div class="sketch-box">
            [ Architecture Sketchpad — Draw your Topology & Traffic Flow Here ]
        </div>
        <div class="page-footer">
            <span>DevOps Master Workbook 2027</span>
            <span>Phase {p} Sheet 3</span>
        </div>
    </div>
    """

final_html = html_template.replace("{PHASES_HTML}", phases_html)

out_path = r"C:\Job Tracker\print\job-tracker.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final_html)

# Also attempt to convert to PDF if wkhtmltopdf or similar is present on windows, or just tell user to print it from chrome.
print("Workbook HTML generated successfully.")
