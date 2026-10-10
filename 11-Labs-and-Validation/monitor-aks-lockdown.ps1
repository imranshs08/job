Write-Host "Monitoring AKS API Server Connectivity..." -ForegroundColor Cyan
Write-Host "Waiting for Zero-Trust Lockdown to take effect (Press Ctrl+C to stop)...`n" -ForegroundColor Yellow

while ($true) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Pinging API Server..." -ForegroundColor DarkGray
    
    # Run kubectl and capture both success and error output
    $output = kubectl get po -A 2>&1
    
    # Check if the error string contains the lockout message
    if ($output -match "Unauthorized" -or $output -match "error: You must be logged in") {
        Write-Host "[$timestamp] 💥 CONNECTIVITY BROKEN! Zero-Trust Lockdown Successful." -ForegroundColor Red
        Write-Host "Server Message: $output" -ForegroundColor DarkRed
        break # Exit the loop
    } else {
        Write-Host "[$timestamp] ✅ Connection Active. Still authenticated..." -ForegroundColor Green
    }
    
    Start-Sleep -Seconds 5
}
