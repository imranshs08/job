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

## 🕒 Scheduling the Report (Cron)
To run this script "Every day at 06 PM, give report to my manager", we use Linux `crontab`.

1. Open your cron editor: `crontab -e`
2. Add the following chronological syntax (06:00 PM = 18:00 Military Time):
```bash
0 18 * * * /bin/bash /opt/devops/aws_resource_tracker.sh > /var/log/aws_tracker.log 2>&1
```

*Syntax Breakdown:*
- `0` = 0th Minute
- `18` = 18th Hour (6 PM)
- `* * *` = Every day of month, every month, every day of week.

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
