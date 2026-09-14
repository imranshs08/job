# 📩 Enabling Logrotate's `mail` Directive (Postfix MTA Setup)

If you simply type `mail audit-logs@yourcompany.com` into your `/etc/logrotate.d/my_app` file, **it will fail silently**. 

Why? Because `logrotate` does not have its own SMTP engine. It blindly pipes the `.gz` payload directly into the local `/usr/bin/mail` Linux binary. If your Linux machine doesn't have a properly configured **Mail Transfer Agent (MTA)** like Postfix or Sendmail running, the email drops into a black hole.

Here is exactly how SREs configure the Linux internal mailer to natively route logs using an enterprise SaaS relay (like your existing `smtp-relay.brevo.com` Brevo account).

---

## 🛠️ Step 1: Install the Mail Utilities

You need the `mailx` binary (which provides the `/usr/bin/mail` command) and the `postfix` MTA daemon to handle the actual routing via SMTP.

```bash
# On RHEL/CentOS/AlmaLinux:
sudo yum install -y postfix mailx cyrus-sasl-plain

# Start and enable the daemon immediately
sudo systemctl enable --now postfix
```

---

## 🔒 Step 2: Configure the SMTP Relay Credentials

We need to tell Postfix *how* to authenticate against your Brevo SMTP server.

```bash
# 1. Create the secure password file
sudo nano /etc/postfix/sasl_passwd

# 2. Inject your SMTP relay and app password in this exact syntax:
# format: [relay_domain]:port user:password
[smtp-relay.brevo.com]:587 b7e208001@smtp-brevo.com:YOUR_SECRET_GMAIL_APP_PASSWORD

# 3. Hash the file into a secure database readable by Postfix
sudo postmap /etc/postfix/sasl_passwd

# 4. Lockdown permissions so non-root users cannot read your SMTP password!
sudo chown root:root /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db
sudo chmod 0600 /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db
```

---

## ⚙️ Step 3: Configure the Postfix Main Architecture

Now we must tell the Postfix daemon to stop trying to deliver internet mail natively (which gets blocked by spam filters) and instead route ALL traffic explicitly through your Brevo relay.

```bash
# Edit the master configuration file
sudo nano /etc/postfix/main.cf
```

Scroll to the bottom of the file and append these enterprise SASL routing rules:
```text
# Force all local /usr/bin/mail traffic directly to the Brevo port
relayhost = [smtp-relay.brevo.com]:587

# Enable SASL authentication
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous

# Ensure TLS encryption is utilized
smtp_tls_security_level = encrypt
smtp_tls_CAfile = /etc/ssl/certs/ca-bundle.crt
```

Save the file and enforce the architecture reload:
```bash
sudo systemctl restart postfix
```

---

## ✅ Step 4: Validate the Relay (The SRE Test)

Before touching `logrotate`, you must ensure the Linux OS can successfully fire out emails.

```bash
# Send an emergency test payload
echo "This is testing the SMTP gateway for Logrotate archives." | mail -s "🚨 Postfix MTA Gateway Test" audit-logs@yourcompany.com
```

If the email successfully hits your inbox, the gateway is primed! 

Now, when `logrotate` triggers and sees the `mail audit@yourcompany.com` directive, it will invoke `/usr/bin/mail`, Postfix will seamlessly capture the `.gz` attachment, authenticate via Brevo, and flawlessly sprint the log file into your auditing inbox exactly 1 millisecond before deleting it from the SSD!
