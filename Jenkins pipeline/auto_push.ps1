$workspace = "C:\Users\HARRISH C\OneDrive\Documents\Antigravity projects\Jenkins pipeline"
cd $workspace

Write-Host "Started auto-push background watcher looking at: $workspace"
Write-Host "Checking every 5 seconds for saved file changes..."
Write-Host "Press Ctrl+C to stop this script."
Write-Host "------------------------------------------------------"

while ($true) {
    # --porcelain gives empty output if there are no changes
    $status = git status --porcelain
    
    if (![string]::IsNullOrEmpty($status)) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Changes detected! Auto-saving to git..."
        git add .
        git commit -m "Auto-commit on save: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git push
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Successfully pushed ✅"
        Write-Host "------------------------------------------------------"
    }
    
    Start-Sleep -Seconds 5
}
