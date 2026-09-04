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

echo "Report successfully generated at $REPORT_FILE"

# NOTE FOR MANAGER EMAIL INTEGRATION:
# You can append standard mailx or mutt commands here to automatically dispatch the report:
# cat $REPORT_FILE | mail -s "Daily AWS Report" manager_email@domain.com
