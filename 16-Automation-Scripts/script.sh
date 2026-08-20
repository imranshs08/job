#!/usr/bin/env bash

# Exit immediately if a pipeline returns a non-zero status
set -uo pipefail

# Output files
CSV_LOG="bank_status_report.csv"
SUMMARY_LOG="summary.txt"

# Initialize files
echo "URL,HTTP_STATUS,RESPONSE_TIME_SEC,EFFECTIVE_URL" > "$CSV_LOG"
> "$SUMMARY_LOG" # Clear previous summary file if it exists

# Timeout configurations (in seconds)
CONNECT_TIMEOUT=5
MAX_TIME=10

# List of Pan-India .bank.in/.env URLs
URLS=(
  # Public Sector Banks
  "https://bankofbaroda.bank.in/.env"
  "https://bankofindia.bank.in/.env"
  "https://bankofmaharashtra.bank.in/.env"
  "https://canarabank.bank.in/.env"
  "https://centralbank.bank.in/.env"
  "https://indianbank.bank.in/.env"
  "https://iob.bank.in/.env"
  "https://punjabandsind.bank.in/.env"
  "https://pnb.bank.in/.env"
  "https://sbi.bank.in/.env"
  "https://ucobank.bank.in/.env"
  "https://unionbankofindia.bank.in/.env"

  # Private Sector Banks
  "https://axis.bank.in/.env"
  "https://bandhan.bank.in/.env"
  "https://cityunionbank.bank.in/.env"
  "https://csb.bank.in/.env"
  "https://dcb.bank.in/.env"
  "https://dhan.bank.in/.env"
  "https://federal.bank.in/.env"
  "https://hdfc.bank.in/.env"
  "https://icici.bank.in/.env"
  "https://idbi.bank.in/.env"
  "https://idfcfirst.bank.in/.env"
  "https://indusind.bank.in/.env"
  "https://jkb.bank.in/.env"
  "https://karnatakabank.bank.in/.env"
  "https://kvb.bank.in/.env"
  "https://kotak.bank.in/.env"
  "https://nainitalbank.bank.in/.env"
  "https://rbl.bank.in/.env"
  "https://southindianbank.bank.in/.env"
  "https://tmb.bank.in/.env"
  "https://yes.bank.in/.env"

  # Small Finance & Payments Banks
  "https://au.bank.in/.env"
  "https://capital.bank.in/.env"
  "https://equitas.bank.in/.env"
  "https://esaf.bank.in/.env"
  "https://fincare.bank.in/.env"
  "https://janasfb.bank.in/.env"
  "https://nesfb.bank.in/.env"
  "https://shivalik.bank.in/.env"
  "https://suryoday.bank.in/.env"
  "https://ujjivansfb.bank.in/.env"
  "https://utkarsh.bank.in/.env"
  "https://airtelpayments.bank.in/.env"
  "https://ippbonline.bank.in/.env"
  "https://fino.bank.in/.env"
  "https://jiopayments.bank.in/.env"
  "https://nsdl.bank.in/.env"
  "https://paytm.bank.in/.env"

  # Foreign Banks
  "https://dbs.bank.in/.env"
  "https://sc.bank.in/.env"
  "https://hsbc.bank.in/.env"
  "https://deutsche.bank.in/.env"
  "https://barclays.bank.in/.env"
)

# Print Header to Console
printf "%-40s | %-12s | %-15s | %-30s\n" "TARGET URL" "STATUS" "TIME (s)" "EFFECTIVE URL"
printf "%s\n" "---------------------------------------------------------------------------------------------------------"

for url in "${URLS[@]}"; do
  # Create a temporary file to store the response body
  TMP_BODY=$(mktemp)

  # Perform curl query
  # -o saves the response payload to the temporary file
  response=$(curl -s -L \
    --connect-timeout "$CONNECT_TIMEOUT" \
    --max-time "$MAX_TIME" \
    -o "$TMP_BODY" \
    -w "%{http_code},%{time_total},%{url_effective}" \
    "$url" 2>/dev/null || echo "000,0.000,$url")

  # Split output fields
  IFS=',' read -r status_code total_time effective_url <<< "$response"

  # Log to summary.txt ONLY if HTTP status is 200
  if [ "$status_code" -eq 200 ]; then
    display_status="200 OK"
    
    # Append a clear header and the HTML response body to summary.txt
    {
      echo "========================================================================"
      echo "URL: $url"
      echo "EFFECTIVE URL: $effective_url"
      echo "DATE: $(date)"
      echo "========================================================================"
      cat "$TMP_BODY"
      echo -e "\n\n"
    } >> "$SUMMARY_LOG"
  elif [ "$status_code" -eq 000 ]; then
    display_status="FAILED/TIMEOUT"
  else
    display_status="HTTP $status_code"
  fi

  # Output to console
  printf "%-40s | %-12s | %-15s | %-30s\n" "$url" "$display_status" "$total_time" "$effective_url"

  # Save to CSV log for record keeping
  echo "$url,$status_code,$total_time,$effective_url" >> "$CSV_LOG"

  # Clean up the temporary file for the next iteration
  rm -f "$TMP_BODY"
done

echo ""
echo "Scan complete."
echo "- CSV Report saved to: $CSV_LOG"
echo "- HTML Responses (200 OK only) saved to: $SUMMARY_LOG"