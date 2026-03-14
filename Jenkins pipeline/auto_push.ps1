$workspace = "C:\Users\HARRISH C\OneDrive\Documents\Antigravity projects\Jenkins pipeline"
Set-Location $workspace

Write-Host "================================================"
Write-Host " Auto-Push Watcher Started"
Write-Host " Watching : $workspace"
Write-Host " Interval : every 5 seconds"
Write-Host " Press Ctrl+C to stop."
Write-Host "================================================"

while ($true) {
    $status = git status --porcelain

    if (![string]::IsNullOrEmpty($status)) {
        $timestamp = Get-Date -Format 'HH:mm:ss'
        Write-Host "[$timestamp] Changes detected — committing..."

        git add .
        git commit -m "Auto-commit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

        # Pull remote changes first to avoid diverged-branch rejections
        Write-Host "[$timestamp] Pulling remote changes (rebase)..."
        $pullResult = git pull --rebase origin main 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[$timestamp] ⚠️  Pull/rebase failed. Skipping push to avoid conflicts:" -ForegroundColor Yellow
            Write-Host $pullResult -ForegroundColor Yellow
        } else {
            $pushResult = git push 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[$timestamp] ✅ Pushed successfully." -ForegroundColor Green
            } else {
                Write-Host "[$timestamp] ❌ Push failed:" -ForegroundColor Red
                Write-Host $pushResult -ForegroundColor Red
            }
        }

        Write-Host "------------------------------------------------"
    }

    Start-Sleep -Seconds 5
}
