import re

def add_profile():
    target_path = r'c:\Job Tracker\index.html'
    
    with open(target_path, 'r', encoding='utf-8') as f:
        html = f.read()

    css_addition = """
        /* ── Profile Identity ── */
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        .cursor-blink { animation: blink 1s step-end infinite; }
    """
    html = html.replace('/* ── Backlog Cards ── */', css_addition + '\n        /* ── Backlog Cards ── */')

    card_html = """
            <!-- Terminal Identity Card -->
            <div class="card" style="--accent: #10b981; --accent-glow: rgba(16, 185, 129, 0.3); grid-column: 1 / -1; margin-bottom: 0;">
                <h2>👨‍💻 <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem;">whoami</span></h2>
                <div style="background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 12px; font-family: 'JetBrains Mono', monospace; border-left: 3px solid #10b981; color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);">
                    <p style="margin-top: 0; color: #10b981;">imran@cmd-center ~ $ <span style="color: #cbd5e1;">cat profile.yaml</span></p>
                    <div style="margin: 0.8rem 0; padding-left: 1rem; border-left: 1px solid rgba(255,255,255,0.1);">
                        <span style="color: #38bdf8;">name:</span> "Imran" <br>
                        <span style="color: #38bdf8;">role:</span> "Cloud & DevOps Engineer" <br>
                        <span style="color: #38bdf8;">mission:</span> "Architecting zero-trust Azure infrastructure and self-healing Kubernetes clusters. Upgrading deployment pipelines with AI-driven operations."<br>
                        <span style="color: #38bdf8;">stack:</span> ["Kubernetes", "Azure", "Terraform", "Docker", "Linux"]<br>
                        <span style="color: #38bdf8;">status:</span> "Deploying to Production (2027 Transition)"
                    </div>
                    <p style="margin-bottom: 0; color: #10b981;">imran@cmd-center ~ $ <span class="cursor-blink" style="color: #cbd5e1;">█</span></p>
                </div>
            </div>

            <!-- Backlog Cards (hidden until populated) -->"""

    html = html.replace('<!-- Backlog Cards (hidden until populated) -->', card_html)

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Profile module injected!")

if __name__ == "__main__":
    add_profile()
