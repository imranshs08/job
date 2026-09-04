# Day-7 | Live AWS Project using SHELL SCRIPTING for DevOps

## 🎯 Project Objective
Write a production-ready Shell Script to report the usage of AWS resources (EC2, S3, IAM, Lambda) and schedule it to execute every day at 06:00 PM via `cron`.

## 🛠️ Key Concepts & AWS CLI Syntax
In Bash, AWS CLI commands require precise subcommands depending on the service API.
- **S3 (Storage):** `aws s3 ls` (Lists all buckets).
- **EC2 (Compute):** `aws ec2 describe-instances` (Note: `aws ec2 ls` is invalid). To extract just the Instance IDs without massive JSON output, we pipe it into `jq`.
- **Lambda (Serverless):** `aws lambda list-functions`.
- **IAM (Identity):** `aws iam list-users`.

> [!IMPORTANT]
> **Defensive Scripting Basics (GEMINI.md Rule)**
> Always start professional Bash scripts with `set -euo pipefail`.
> - `-e`: Exits immediately if any command fails.
> - `-u`: Exits if trying to use an uninitialized variable.
> - `-o pipefail`: Exits if any command within a `|` pipeline fails.

## 🕒 Scheduling the Report (Cron and Crontab Deep Dive)
In Linux, **Cron** is a daemon (background service) that automatically runs scripts or commands at specified times and dates. **Crontab** (Cron Table) is the configuration file that tells the Cron daemon *what* to run and *when* to run it.

### Core Crontab Commands
To interact with your user's specific cron jobs, use the `crontab` binary:
- `crontab -e`: Edits your current crontab file (opens in `vi` or `nano`).
- `crontab -l`: Lists all currently scheduled cron jobs.
- `crontab -r`: Removes/deletes your entire crontab (Use with extreme caution!).

### The Cron Syntax Formula
A cron job is defined by 5 asterisks followed by the execution command.
It follows this exact pattern: `* * * * * command_to_execute`
1. **Minute** (0 - 59)
2. **Hour** (0 - 23) *Military time*
3. **Day of Month** (1 - 31)
4. **Month** (1 - 12)
5. **Day of Week** (0 - 7) *(0 and 7 are both Sunday)*

### 🚀 Practical Crontab Examples
Here are common scheduling patterns you will likely encounter in DevOps interviews:

1. **Every day at 06:00 PM (Our Project Goal):**
   ```bash
   0 18 * * * /bin/bash /opt/devops/aws_resource_tracker.sh
   # Translates to: 0th Minute | 18th Hour | Every Day | Every Month | Every Day of the Week
   ```
2. **Every 5 minutes, 24/7:**
   ```bash
   */5 * * * * /bin/bash /opt/check_health.sh
   # The "*/5" syntax means "every 5th interval".
   ```
3. **Every Sunday strictly at Midnight:**
   ```bash
   0 0 * * 0 /bin/bash /opt/weekly_backup.sh
   # Translates to: 00:00 (Midnight) | Every Day | Every Month | ONLY on Sunday (0)
   ```
4. **Every Weekday (Monday - Friday) at 9:00 AM:**
   ```bash
   0 9 * * 1-5 /bin/bash /opt/start_instances.sh
   # 1-5 denotes Monday through Friday.
   ```

> [!WARNING]
> **Cron Environment Limitations:**
> Cron does NOT load your standard environment variables (like `$PATH` or AWS credentials). You must always use **absolute paths** to your executables (e.g., `/bin/bash` instead of just `bash`, and `/usr/local/bin/aws` instead of just `aws`) OR export your variables at the top of your bash script!

---

## 📝 Sample Reference Script (aws_resource_tracker.sh)
Below is the full implementation script that includes defensive Bash constraints and structured JSON object extraction formatting:

```bash
#!/bin/bash
# ==============================================================================
# Author : Imran 
# Date : 04-Sep-2026
# Email : imranshs08@gmail.com
# Version : 1.0 (Production)
# Description : AWS Daily Usage Tracker (S3, EC2, Lambda, IAM)
# ==============================================================================

# Defensive Scripting: Fail fast on errors, undefined variables, and pipe failures
set -euo pipefail

# In Cron environments, AWS CLI might not be in the default PATH. Exporting it explicitly:
export PATH=/usr/local/bin:/usr/bin:$PATH

REPORT_FILE="/tmp/aws_daily_report_$(date '+%Y-%m-%d').txt"

echo "==========================================================" > "$REPORT_FILE"
echo " AWS DAILY RESOURCE USAGE REPORT " >> "$REPORT_FILE"
echo " Date Generated: $(date)" >> "$REPORT_FILE"
echo "==========================================================" >> "$REPORT_FILE"

echo -e "\n[+] 1. Extracting Active S3 Buckets..." >> "$REPORT_FILE"
# Extract only the bucket names
aws s3 ls | awk '{print $3}' >> "$REPORT_FILE" || echo "Error fetching S3." >> "$REPORT_FILE"

echo -e "\n[+] 2. Extracting Provisioned EC2 Instances..." >> "$REPORT_FILE"
# Extract only the Instance IDs using jq
aws ec2 describe-instances | jq -r '.Reservations[].Instances[].InstanceId' >> "$REPORT_FILE" || echo "Error fetching EC2." >> "$REPORT_FILE"

echo -e "\n[+] 3. Extracting Lambda Functions..." >> "$REPORT_FILE"
# Extract only Function Names
aws lambda list-functions | jq -r '.Functions[].FunctionName' >> "$REPORT_FILE" || echo "Error fetching Lambda." >> "$REPORT_FILE"

echo -e "\n[+] 4. Extracting IAM Users..." >> "$REPORT_FILE"
aws iam list-users | jq -r '.Users[].UserName' >> "$REPORT_FILE" || echo "Error fetching IAM." >> "$REPORT_FILE"

echo -e "\n==========================================================" >> "$REPORT_FILE"
echo " End of Report." >> "$REPORT_FILE"
```
