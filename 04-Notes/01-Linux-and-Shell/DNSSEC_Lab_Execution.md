# 🔐 SRE Execution Lab: Resolving a DNSSEC Outage

This lab explicitly requires you to provision two isolated Linux machines on a private Azure Subnet, completely break the cryptographic trust anchor on the gateway server, and witness the catastrophic impact on the connected client.

> [!TIP]
> We will specifically deploy in `centralus` instead of `eastus` to explicitly bypass your active 4-core limit Quota bounds!

---

## 🏗️ Phase 1: Dual-VM Provisioning (Azure Cloud Shell)

Run these exact strings from your Azure Cloud Shell natively:

```bash
# 1. Create a dedicated Resource Group in a clean region
az group create --name rg-dnssec-lab --location centralus

# 2. Deploy the isolated Virtual Network structure
az network vnet create -g rg-dnssec-lab -n vnet-dnssec \
    --address-prefix 10.0.0.0/16 --subnet-name snet-internal --subnet-prefix 10.0.1.0/24

# 3. Provision the upstream DNS Server Gateway
az vm create -g rg-dnssec-lab -n vm-dns-server \
    --vnet-name vnet-dnssec --subnet snet-internal \
    --image Ubuntu2204 --admin-username sreadmin --admin-password "SreDevOps2027!" \
    --public-ip-sku Standard --size Standard_B1s

# 4. Provision the downstream App Client
az vm create -g rg-dnssec-lab -n vm-dns-client \
    --vnet-name vnet-dnssec --subnet snet-internal \
    --image Ubuntu2204 --admin-username sreadmin --admin-password "SreDevOps2027!" \
    --public-ip-sku Standard --size Standard_B1s

# 5. Extract the IP Addresses (Save these!)
az vm list-ip-addresses -g rg-dnssec-lab -o table
```

---

## 💥 Phase 2: Installing and Sabotaging the Target Server

SSH directly into the **`vm-dns-server`**:
```bash
ssh sreadmin@[VM-DNS-SERVER-PUBLIC-IP]
```

### Enable DNS and Corrupt the Keystore
```bash
# Install the DNS caching software
sudo apt update && sudo apt install bind9 dnsutils -y

# Corrupt the Root Zone Keys (Sabotage!)
sudo bash -c 'echo "managed-keys { \".\" initial-key 257 3 8 \"AwEAAAABBBBBCCCCCDDDDDEEEEEFFFFFGGGGGHHHHHIIIIIJJJJJKKKKKLLLLLMMMMMNNNNNOOOOOPPPPPQQQQQRRRRRSSSSSTTTTTUUUUUVVVVVWWWWWXXXXXYYYYYZZZZZ\"; };" > /etc/bind/bind.keys'

# Hard-enforce DNSSEC validation to refuse to fall back.
sudo sed -i 's/dnssec-validation auto;/dnssec-validation yes;/g' /etc/bind/named.conf.options

# Lock in the broken state
sudo systemctl restart bind9
```

---

## 🚨 Phase 3: The Impact (Negative Validation)

Open a **new** terminal window and SSH into the downstream **`vm-dns-client`**:
```bash
ssh sreadmin@[VM-DNS-CLIENT-PUBLIC-IP]
```

### Route Client to Corrupted Gateway
```bash
# Force the Linux kernel to drop 168.63.129.16 (Azure DNS) and use your server natively
sudo resolvectl dns eth0 [VM-DNS-SERVER-PRIVATE-IP]
sudo resolvectl default-route eth0 true
```

### Execute the DNS Test 
```bash
# Query the internet
dig google.com
```

> [!WARNING]
> This command will throw **SERVFAIL**. The downstream client cannot connect to the internet because the DNS server cryptographically rejected the packet signatures natively!

---

## ⚕️ Phase 4: SRE Forensic Fix & Recovery (Positive Validation)

Switch your terminal back to the **`vm-dns-server`**:

```bash
# Dynamically fetch the official ICANN Trust Anchor via root protocols natively.
wget -qO- https://data.iana.org/root-anchors/bind.keys | sudo tee /etc/bind/bind.keys

# Restart the DNS Gateway Service
sudo systemctl restart bind9
```

### The Ultimate Validation
Switch back to your **`vm-dns-client`** terminal and re-run your `dig`:
```bash
dig google.com
```
You will immediately receive an active IP list natively, but more importantly, look at the DNS header:
`flags: qr rd ra ad;`

The `ad` (Authenticated Data) flag mathematically proves that your newly integrated DNSSEC trust anchor has successfully restored internet routing for all internal clients!
