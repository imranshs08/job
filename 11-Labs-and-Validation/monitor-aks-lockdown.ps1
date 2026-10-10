Write-Host "Monitoring AKS API Server Connectivity..." -ForegroundColor Cyan
Write-Host "Waiting for Zero-Trust Lockdown to take effect (Press Ctrl+C to stop)...`n" -ForegroundColor Yellow

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$attempts = 1

while ($true) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $elapsed = $stopwatch.Elapsed
    # Format elapsed time as MM:SS
    $elapsedStr = [string]::Format("{0:00}:{1:00}:{2:00}", [math]::Floor($elapsed.TotalHours), $elapsed.Minutes, $elapsed.Seconds)
    
    Write-Host "[$timestamp] [Elapsed: $elapsedStr] (Attempt $attempts) Pinging API Server..." -ForegroundColor DarkGray
    
    # Run kubectl and capture both success and error output
    $output = kubectl get po -A 2>&1
    
    # Check if the error string contains the lockout message
    if ($output -match "Unauthorized" -or $output -match "error: You must be logged in") {
        Write-Host "`n[$timestamp] 💥 CONNECTIVITY BROKEN! Zero-Trust Lockdown Successful." -ForegroundColor Red
        Write-Host "Total Time to Lockdown: $($elapsed.Minutes) minutes and $($elapsed.Seconds) seconds." -ForegroundColor Red
        Write-Host "Server Message: $output" -ForegroundColor DarkRed
        break # Exit the loop
    }
    else {
        Write-Host "[$timestamp] ✅ Connection Active. Still authenticated..." -ForegroundColor Green
    }
    
    $attempts++
    Start-Sleep -Seconds 5
}
