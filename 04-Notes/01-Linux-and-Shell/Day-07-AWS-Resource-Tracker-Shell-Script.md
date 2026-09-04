# Day-7 | Live AWS Project using SHELL SCRIPTING for DevOps

## í¾¯ Project Objective
Write a production-ready Shell Script to report the usage of AWS resources (EC2, S3, IAM, Lambda) and schedule it to execute every day at 06:00 PM via `cron`.

## í» ï¸ Key Concepts & AWS CLI Syntax
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

## íµ’ Scheduling the Report (Cron)
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
