import re

html_file = r"c:\Job Tracker\aks-expert-viewer.html"
with open(html_file, "r", encoding="utf-8") as f:
    base_html = f.read()

top_html = base_html.split('<div class="section-label">')[0]
footer_html = base_html[base_html.find('<footer>'):]

top_html = top_html.replace("AKS Made Easy Dashboard", "DNSSEC KSK Outage Simulator (SRE Lab)")
top_html = top_html.replace("AKS Made Easy 20-Day Mastery", "SRE Catastrophe Recovery Lab")
top_html = top_html.replace("AKS Masterclass", "DNSSEC & BIND9")
top_html = top_html.replace("A 20-Day intensive deep dive into AKS starting from fundamentals to advanced Gateway, Security, and Azure DevOps integration.", "A highly-structured Chaos Engineering lab simulating a lethal Cryptographic Trust Anchor collapse (ICANN KSK Rollover failure) utilizing Dual-VM Azure Native VNETs.")
top_html = top_html.replace('<div class="stat-value">20</div>\n            <div class="stat-label">Total Days</div>', '<div class="stat-value">5</div>\n            <div class="stat-label">SRE Execution Phases</div>')
top_html = top_html.replace('<div class="stat-value">19.5</div>\n            <div class="stat-label">Hours</div>', '<div class="stat-value">45</div>\n            <div class="stat-label">Minutes (SLA)</div>')

phases = [
    ("Phase 1: Dual-VM Provisioning", "Execute from Azure Cloud Shell to aggressively bypass local limitations and autonomously build the topology.", "dnssec-phase1.html"),
    ("Phase 2: Gateway Sabotage", "SSH into the server and violently corrupt ICANN root keys, fundamentally blocking the validation chain.", "dnssec-phase2.html"),
    ("Phase 3: The Impact (SERVFAIL)", "Route the downstream client into the damaged DNS config and systematically log the catastrophic dropout.", "dnssec-phase3.html"),
    ("Phase 4: SRE Forensic Recovery", "Operate directly on the server to dynamically pull native ICANN keys over an unauthenticated HTTPs tunnel.", "dnssec-phase4.html"),
    ("Phase 5: The Ultimate Validation", "Jump back into the internal app cluster and forcefully validate that recursive routing is fully restored.", "dnssec-phase5.html")
]

cards_html = ""
for title, desc, link in phases:
    cards_html += f'''
        <div class="card" onclick="window.location.href='{link}'" style="cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 0 15px rgba(52, 211, 153, 0.4)'" onmouseout="this.style.boxShadow=''">
            <div class="card-icon" style="position:relative;">🔐</div>
            <h2>{title}</h2>
            <p>{desc}</p>
            <div class="video-list">
                <a class="video-link" style="color: #38bdf8; text-decoration: underline;">Launch Phase Guide ➔</a>
            </div>
        </div>
    '''

middle_html = f'<div class="section-label">📚 The DNSSEC Execution Vector</div>\n    <div class="grid">\n{cards_html}    </div>\n'
main_page_html = top_html + middle_html + footer_html
main_page_html = main_page_html.replace('DNSSEC SRE Command Center', 'DNSSEC SRE Tracker')

with open(r"c:\Job Tracker\dnssec-sre-lab.html", "w", encoding="utf-8") as f:
    f.write(main_page_html)

phase_data = {
    1: {
        "title": "Phase 1: Dual-VM Provisioning",
        "concept": "To accurately simulate global routing collapse, we must first provision a private Azure Virtual Network (VNet). <br><br>We deploy two Linux nodes within this <b>snet-internal</b> block: <br>1. <b>vm-dns-server</b>: The authoritative gateway running BIND9.<br>2. <b>vm-dns-client</b>: The application node that consumes the gateway.",
        "commands": [
            ('az group create --name rg-dnssec-lab --location centralus', 0),
            ('az network vnet create -g rg-dnssec-lab -n vnet-dnssec --address-prefix 10.0.0.0/16 --subnet-name snet-internal --subnet-prefix 10.0.1.0/24', 0),
            ('az vm create -g rg-dnssec-lab -n vm-dns-server --vnet-name vnet-dnssec --subnet snet-internal --image Ubuntu2204 --admin-username sreadmin --admin-password "SreDevOps2027!" --public-ip-sku Standard --size Standard_B1s', 0),
            ('az vm create -g rg-dnssec-lab -n vm-dns-client --vnet-name vnet-dnssec --subnet snet-internal --image Ubuntu2204 --admin-username sreadmin --admin-password "SreDevOps2027!" --public-ip-sku Standard --size Standard_B1s', 0),
            ('Export identical topological ENV variables into your current Azure CLI session:', 1),
            ('export SERVER_PUBLIC_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-server --query publicIps -o tsv)', 0),
            ('export SERVER_PRIVATE_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-server --query privateIps -o tsv)', 0),
            ('export CLIENT_PUBLIC_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-client --query publicIps -o tsv)', 0),
            ('echo -e "Server: $SERVER_PUBLIC_IP\nClient: $CLIENT_PUBLIC_IP\nServer_PRI: $SERVER_PRIVATE_IP"', 0)
        ]
    },
    2: {
        "title": "Phase 2: Gateway Sabotage",
        "concept": "Modern resolvers ship with valid ICANN Trust Anchors embedded in their configuration files. In this phase, we act as a malicious threat actor or decaying shadow infrastructure. <br><br>We will aggressively overwrite the <code>bind.keys</code> trust anchor block with completely corrupted RSA signatures and forcefully lock BIND9 into high-enforcement mode.",
        "commands": [
            ('ssh sreadmin@$SERVER_PUBLIC_IP', 1),
            ('sudo apt update && sudo apt install bind9 dnsutils -y', 0),
            ('sudo bash -c \'echo "managed-keys { \\".\\" initial-key 257 3 8 \\"AwEAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGGHHHHHIIIIIJJJJJKKKKKLLLLLMMMMM...\\"; };" > /etc/bind/bind.keys\'', 0),
            ("sudo sed -i 's/dnssec-validation auto;/dnssec-validation yes;/g' /etc/bind/named.conf.options", 0),
            ("sudo systemctl restart bind9", 0)
        ]
    },
    3: {
        "title": "Phase 3: The Cryptographic Impact",
        "concept": "The client server is configured to natively resolve against Azure's global DNS (168.63.129.16). We must manipulate the local internal Linux routing table using <code>resolvectl</code> to force the client to consume our corrupted DNS Server instead. <br><br>The instant we query an external payload like Google, the validation chain shatters resulting in a fatal SERVFAIL.",
        "commands": [
            ('NOTE: Before SSHing into the client, you must carry forward the Server Private IP:', 1),
            ('export CLIENT_PUBLIC_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-client --query publicIps -o tsv)', 0),
            ('export SERVER_PRIVATE_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-server --query privateIps -o tsv)', 0),
            ('ssh sreadmin@$CLIENT_PUBLIC_IP', 1),
            ('sudo resolvectl dns eth0 $SERVER_PRIVATE_IP  # DO NOT OMIT THIS!', 0),
            ('sudo resolvectl default-route eth0 true', 0),
            ('dig google.com # YOU MUST WITNESS THE SERVFAIL EXCEPTION!', 1)
        ]
    },
    4: {
        "title": "Phase 4: SRE Forensic Recovery",
        "concept": "The internet is down, applications are crashing, and the cache TTLs have expired. How do you recover? <br><br>Since the internal DNS resolver cannot recursively trace domains, you must rely on hardcoded IP tunnels. However, a safer path is simply bypassing recursive hooks and relying on core network HTTPS resolution. <br><br>We pull the official Root Anchor XML natively from IANA, overwriting the corrupted block.",
        "commands": [
            ('Return to your `vm-dns-server` SSH terminal session directly:', 1),
            ('wget -qO- https://data.iana.org/root-anchors/bind.keys | sudo tee /etc/bind/bind.keys', 0),
            ('sudo systemctl restart bind9', 0)
        ]
    },
    5: {
        "title": "Phase 5: The Ultimate Validation",
        "concept": "We must verify mathematical cryptographic compliance. When we query Google again, pay excruciating attention to the DNS headers.<br><br>The presence of the <b>ad</b> (Authenticated Data) flag implies that the recursive server has successfully processed the upstream zone-signing key and verified it recursively against your fr
