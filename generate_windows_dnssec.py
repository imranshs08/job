import re
import os

html_file = r"c:\Job Tracker\aks-expert-viewer.html"
with open(html_file, "r", encoding="utf-8") as f:
    base_html = f.read()

top_html_home = base_html.split('<div class="section-label">')[0]
footer_html = base_html[base_html.find('<footer>'):]
top_html_home = top_html_home.replace("AKS Made Easy Dashboard", "DNSSEC KSK Outage Simulator (SRE Lab)")
top_html_home = top_html_home.replace("AKS Made Easy 20-Day Mastery", "SRE Catastrophe Recovery Lab")
top_html_home = top_html_home.replace("AKS Masterclass", "DNSSEC & BIND9")
top_html_home = top_html_home.replace("A 20-Day intensive deep dive into AKS starting from fundamentals to advanced Gateway, Security, and Azure DevOps integration.", "A highly-structured Chaos Engineering lab simulating a lethal Cryptographic Trust Anchor collapse (ICANN KSK Rollover failure) utilizing Dual-VM Azure Native VNETs.")
top_html_home = top_html_home.replace('<div class="stat-value">20</div>\n            <div class="stat-label">Total Days</div>', '<div class="stat-value">5</div>\n            <div class="stat-label">SRE Execution Phases</div>')
top_html_home = top_html_home.replace('<div class="stat-value">19.5</div>\n            <div class="stat-label">Hours</div>', '<div class="stat-value">45</div>\n            <div class="stat-label">Minutes (SLA)</div>')

nav_end_idx = base_html.find('</nav>') + 6
top_nav_only = base_html[:nav_end_idx]
top_nav_only = top_nav_only.replace("AKS Made Easy Dashboard", "DNSSEC KSK Outage Simulator (SRE Lab)")

phases = [
    ("Phase 1: Dual-OS Provisioning", "Execute from Azure Cloud Shell to aggressively bypass local limitations and autonomously build the topology.", "dnssec-phase1.html"),
    ("Phase 2: Gateway Sabotage", "SSH into the Linux Server and violently corrupt ICANN root keys, fundamentally blocking the validation chain.", "dnssec-phase2.html"),
    ("Phase 3: The Impact (SERVFAIL)", "RDP into the Windows client, hijack the NIC via PowerShell to lock to the broken gateway, overriding Azure.", "dnssec-phase3.html"),
    ("Phase 4: Forensic Recovery", "Operate directly on the Linux server to dynamically pull native ICANN keys over an unauthenticated HTTPs tunnel.", "dnssec-phase4.html"),
    ("Phase 5: Powershell Validation", "Jump back into the Windows Server and leverage Resolve-DnsName to mathematically confirm the chain is healthy.", "dnssec-phase5.html")
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

middle_html = f'<div class="section-label">📚 The DNSSEC Execution Vector (Enterprise Topography)</div>\n    <div class="grid">\n{cards_html}    </div>\n'
main_page_html = top_html_home + middle_html + footer_html
main_page_html = main_page_html.replace('DNSSEC SRE Command Center', 'DNSSEC SRE Tracker')

with open(r"c:\Job Tracker\dnssec-sre-lab.html", "w", encoding="utf-8") as f:
    f.write(main_page_html)

phase_data = {
    1: {
        "title": "Phase 1: Dual-OS Provisioning",
        "concept": "To accurately simulate global routing collapse inside an Enterprise active-directory structure, we must provision a cross-platform Private Virtual Network. <br><br>We deploy two nodes: <br>1. <b>vm-dns-server</b>: The authoritative Linux gateway running BIND9.<br>2. <b>vm-dns-client</b>: The native Windows Server 2022 downstream app node.",
        "commands": [
            ('az group create --name rg-dnssec-lab --location centralus', 0),
            ('az network vnet create -g rg-dnssec-lab -n vnet-dnssec --address-prefix 10.0.0.0/16 --subnet-name snet-internal --subnet-prefix 10.0.1.0/24', 0),
            ('az vm create -g rg-dnssec-lab -n vm-dns-server --vnet-name vnet-dnssec --subnet snet-internal --image Ubuntu2204 --admin-username sreadmin --admin-password "SreDevOps2027!" --public-ip-sku Standard --size Standard_D2s_v7', 0),
            ('az vm create -g rg-dnssec-lab -n vm-dns-client --vnet-name vnet-dnssec --subnet snet-internal --image Win2022Datacenter --admin-username sreadmin --admin-password "SreDevOps2027!" --public-ip-sku Standard --size Standard_D2s_v7', 0),
            ('Verify Server Deployment:', 1),
            ('az vm show -g rg-dnssec-lab -n vm-dns-server -d --query "provisioningState" -o tsv', 0),
            ('Verify OS Client Deployment:', 1),
            ('az vm show -g rg-dnssec-lab -n vm-dns-client -d --query "provisioningState" -o tsv', 0),
            ('Extract environmental topology variables straight into your current Shell namespace:', 1),
            ('export SERVER_PUBLIC_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-server --query publicIps -o tsv)', 0),
            ('export SERVER_PRIVATE_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-server --query privateIps -o tsv)', 0),
            ('export CLIENT_PUBLIC_IP=$(az vm show -d -g rg-dnssec-lab -n vm-dns-client --query publicIps -o tsv)', 0),
            ('echo -e "Linux Server: $SERVER_PUBLIC_IP | Private: $SERVER_PRIVATE_IP | Windows Client (RDP): $CLIENT_PUBLIC_IP"', 0)
        ]
    },
    2: {
        "title": "Phase 2: Gateway Sabotage",
        "concept": "Modern resolvers ship with valid ICANN Trust Anchors embedded in their configuration files. In this phase, we act as a malicious threat actor or decaying shadow infrastructure. <br><br>We will aggressively overwrite the <code>bind.keys</code> trust anchor block with completely corrupted RSA signatures and forcefully lock Linux BIND9 into high-enforcement mode.",
        "commands": [
            ('ssh sreadmin@$SERVER_PUBLIC_IP', 1),
            ('sudo apt update && sudo apt install bind9 dnsutils -y', 0),
            ('sudo bash -c \'echo "managed-keys { \\".\\" initial-key 257 3 8 \\"AwEAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGGHHHHHIIIIIJJJJJKKKKKLLLLLMMMMM...\\"; };" > /etc/bind/bind.keys\'', 0),
            ("sudo sed -i 's/dnssec-validation auto;/dnssec-validation yes;/g' /etc/bind/named.conf.options", 0),
            ("sudo systemctl restart bind9", 0)
        ]
    },
    3: {
        "title": "Phase 3: The Windows Cryptographic Impact",
        "concept": "<b>[ 🛑 NEGATIVE VALIDATION TEST ]</b><br>The Windows Client organically bypasses the broken gateway using Azure DHCP. We must manually hijack the NIC utilizing strict PowerShell evaluation protocols to definitively trigger the routing collapse.<br><br>Because Windows aggressively checks native ICANN chains locally on modern implementations, enforcing DNSSEC across a sabotaged gateway will force the PowerShell cmdlet to vomit a literal <b>DNS server failure</b> Exception—mathematically identical to a Linux <code>SERVFAIL</code>.",
        "commands": [
            ('Connect to this Windows Public IP using Remote Desktop Desktop Connection (mstsc.exe):', 1),
            ('echo "Windows RDP Public Target: $CLIENT_PUBLIC_IP"', 0),
            ('Open PowerShell as Administrator inside the Windows RDP Session and Hijack the NIC:', 1),
            ('Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses <INSERT_SERVER_PRIVATE_IP>', 0),
            ('Clear-DnsClientCache', 0),
            ('Wait for the NIC flush (10 seconds), then explicitly enforce strict DNSSEC packet checking:', 1),
            ('Resolve-DnsName -Name google.com -DnssecOk -Server <INSERT_SERVER_PRIVATE_IP>', 0),
            ('🛑 NEGATIVE OUTCOME EVALUATION:', 1),
            ('The screen MUST flash red and output: "Resolve-DnsName : google.com : DNS server failure". This explicitly confirms cryptographic trust isolation.', 1)
        ]
    },
    4: {
        "title": "Phase 4: Forensic Recovery",
        "concept": "The Windows Domain apps ar
