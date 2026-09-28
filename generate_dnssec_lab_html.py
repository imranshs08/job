html_file = r"c:\Job Tracker\aks-expert-viewer.html"
with open(html_file, "r", encoding="utf-8") as f:
    base_html = f.read()

top_html = base_html.split('<div class="section-label">')[0]
footer_html = base_html[base_html.find('<footer>'):]

top_html = top_html.replace("AKS Made Easy Dashboard", "DNSSEC KSK Outage Simulator (SRE Lab)")
top_html = top_html.replace("AKS Made Easy 20-Day Mastery", "SRE Catastrophe Recovery Lab")
top_html = top_html.replace("AKS Masterclass", "DNSSEC & BIND9")
top_html = top_html.replace("A 20-Day intensive deep dive into AKS starting from fundamentals to advanced Gateway, Security, and Azure DevOps integration.", "A highly-structured Chaos Engineering lab simulating a lethal Cryptographic Trust Anchor collapse (ICANN KSK Rollover failure) utilizing Dual-VM Azure Native VNETs.")
top_html = top_html.replace('<div class="stat-value">20</div>\n            <div class="stat-label">Total Days</div>', '<div class="stat-value">6</div>\n            <div class="stat-label">SRE Execution Phases</div>')
top_html = top_html.replace('<div class="stat-value">19.5</div>\n            <div class="stat-label">Hours</div>', '<div class="stat-value">45</div>\n            <div class="stat-label">Minutes (SLA)</div>')

phases = [
    (
        "Phase 1: Dual-VM Provisioning", 
        "Execute from Azure Cloud Shell to aggressively bypass local limitations and autonomously build the topology.",
        "▶ ⏱️ Terminal Cloud Execution Commands",
        [
            ("az group create --name rg-dnssec-lab --location centralus", 0),
            ("az network vnet create -g rg-dnssec-lab -n vnet-dnssec --address-prefix 10.0.0.0/16 --subnet-name snet-internal --subnet-prefix 10.0.1.0/24", 0),
            ("az vm create -g rg-dnssec-lab -n vm-dns-server --vnet-name vnet-dnssec --subnet snet-internal --image Ubuntu2204 --admin-username sreadmin --admin-password SreDevOps2027! --public-ip-sku Standard --size Standard_B1s", 0),
            ("az vm create -g rg-dnssec-lab -n vm-dns-client --vnet-name vnet-dnssec --subnet snet-internal --image Ubuntu2204 --admin-username sreadmin --admin-password SreDevOps2027! --public-ip-sku Standard --size Standard_B1s", 0)
        ]
    ),
    (
        "Phase 2: Sabotaging the Target Server", 
        "SSH into the gateway and inject heavily corrupted ICANN root keys, fundamentally blocking the validation chain.",
        "▶ 🔧 Terminal Gateway Sabotage (vm-dns-server)",
        [
            ("ssh sreadmin@[VM-DNS-SERVER-PUBLIC-IP]", 1),
            ("sudo apt update && sudo apt install bind9 dnsutils -y", 0),
            ("""sudo bash -c 'echo "managed-keys { \\".\\" initial-key 257 3 8 \\"AwEAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGGHHHHHIIIIIJJJJJKKKKKLLLLLMMMMM...\\"; };" > /etc/bind/bind.keys'""", 0),
            ("sudo sed -i 's/dnssec-validation auto;/dnssec-validation yes;/g' /etc/bind/named.conf.options", 0),
            ("sudo systemctl restart bind9", 0)
        ]
    ),
    (
        "Phase 3: The Impact (Negative Validation)", 
        "Route the downstream client into the damaged DNS configuration and systematically observe the catastrophic internet dropout.",
        "▶ 📉 Terminal Client Impact (vm-dns-client)",
        [
            ("ssh sreadmin@[VM-DNS-CLIENT-PUBLIC-IP]", 1),
            ("sudo resolvectl dns eth0 [VM-DNS-SERVER-PRIVATE-IP]", 0),
            ("sudo resolvectl default-route eth0 true", 0),
            ("dig google.com # YOU MUST WITNESS THE SERVFAIL EXCEPTION!", 1)
        ]
    ),
    (
        "Phase 4: SRE Forensic Fix & Recovery", 
        "Operate directly on the server to dynamically pull native ICANN keys over an unauthenticated HTTPs tunnel.",
        "▶ ⚕️ Terminal Native Recovery (vm-dns-server)",
        [
            ("wget -qO- https://data.iana.org/root-anchors/bind.keys | sudo tee /etc/bind/bind.keys", 0),
            ("sudo systemctl restart bind9", 0)
        ]
    ),
    (
        "Phase 5: The Ultimate Validation", 
        "Jump back into the internal application cluster node and forcefully validate that upstream web resolution is operational.",
        "▶ ✅ Final Protocol Resolution (vm-dns-client)",
        [
            ("dig google.com", 0),
            ("Look for the NOERROR block alongside the flags: qr rd ra [ad];", 1)
        ]
    )
]

cards_html = ""
for title, desc, acc_title, cmds in phases:
    cmds_html = ""
    for cmd, is_comment in cmds:
        if is_comment:
            cmds_html += f'<li style="font-size: 0.85em; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 6px; color:#38bdf8;"># {cmd}</li>\n'
        else:
            cmds_html += f'<li style="font-size: 0.85em; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 6px; font-family:monospace; color:#bae6fd;">$ {cmd}</li>\n'
            
    cards_html += f'''
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div class="card-icon" style="position:relative;">🔐</div>
                <label style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; cursor: pointer; color: #94a3b8; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 12px; transition: 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='rgba(0,0,0,0.2)'">
                    <input type="checkbox" class="day-checkbox" style="accent-color: #34d399; width: 14px; height: 14px; cursor: pointer;">
                    Validated
                </label>
            </div>
            <h2>{title}</h2>
            <p>{desc}</p>
            <div class="video-details" style="margin-top: 1rem;">
                <details style="background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 8px; padding: 0.5rem;" open>
                    <summary style="cursor: pointer; font-size: 0.9em; font-weight: 500; color: #bae6fd;">{acc_title}</summary>
                    <ul style="list-style: none; padding: 0.5rem 0 0 0; margin: 0; background-color: #0f172a; padding: 10px; border-radius: 6px; overflow-x: auto;">
                        {cmds_html}
                    </ul>
                </details>
            </div>
        </div>
    '''

middle_html = f'''<div class="section-label">📚 The DNSSEC Execution Vector</div>
    <div class="grid">
{cards_html}    </div>
    <!-- END CRAM GRID -->
'''

new_html = top_html + middle_html + footer_html
new_html = new_html.replace('aks-made-easy-sprint.md', 'DNSSEC_Lab_Execution.md')
new_html = new_html.replace('AKS Sprint Tracker', 'DNSSEC SRE Command Center')

with open(r"c:\Job Tracker\dnssec-sre-lab.html", "w", encoding="utf-8") as f:
    f.write(new_html)
print("DNSSEC SRE HTML UI generated successfully.")
