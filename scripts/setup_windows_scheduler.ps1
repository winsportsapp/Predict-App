# PowerShell script to register Predict App automatic match sync in Windows Task Scheduler
# Run this script as Administrator or standard user to automate syncs.

$ProjectDir = (Get-Item $PSScriptRoot\..).FullName
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$SyncRunner = Join-Path $ProjectDir "scripts\run_scheduled_sync.ps1"
$PowerShellExe = "powershell.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment python.exe not found at $VenvPython"
    exit 1
}

if (-not (Test-Path $SyncRunner)) {
    Write-Error "Sync runner script not found at $SyncRunner"
    exit 1
}

Write-Host "Registering Predict App Scheduled Tasks with Battery & Catch-up Resilience..." -ForegroundColor Cyan
Write-Host "Project Directory: $ProjectDir"
Write-Host "Runner Script:     $SyncRunner"

# Configure Task Scheduler settings:
# - AllowStartIfOnBatteries: Run even if laptop is on battery power
# - DontStopIfGoingOnBatteries: Don't kill task if unplugged during run
# - StartWhenAvailable: Catch up missed runs if laptop was asleep/off at 06:30 or 20:30
# - WakeToRun: Wake system if in modern standby
# - Priority 4: Normal process priority
# - ExecutionTimeLimit: 30 minutes max
# - MultipleInstances: IgnoreNew
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -Priority 4 `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -MultipleInstances IgnoreNew

# 1. Morning Results Sync (06:30 IST)
$Action1 = New-ScheduledTaskAction -Execute $PowerShellExe -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$SyncRunner`" -ActionType results -Slot 06:30" -WorkingDirectory $ProjectDir
$Trigger1 = New-ScheduledTaskTrigger -Daily -At "06:30AM"
Register-ScheduledTask -TaskName "PredictApp_Morning_Results_0630" -Action $Action1 -Trigger $Trigger1 -Settings $Settings -Description "Predict App Morning Match Results Sync (06:30 IST)" -Force

# 2. Morning Fixtures Sync (06:35 IST)
$Action2 = New-ScheduledTaskAction -Execute $PowerShellExe -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$SyncRunner`" -ActionType fixtures -Slot 06:30" -WorkingDirectory $ProjectDir
$Trigger2 = New-ScheduledTaskTrigger -Daily -At "06:35AM"
Register-ScheduledTask -TaskName "PredictApp_Morning_Fixtures_0635" -Action $Action2 -Trigger $Trigger2 -Settings $Settings -Description "Predict App Morning Fixtures & Odds Sync (06:35 IST)" -Force

# 3. Evening Results Sync (20:30 IST)
$Action3 = New-ScheduledTaskAction -Execute $PowerShellExe -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$SyncRunner`" -ActionType results -Slot 20:30" -WorkingDirectory $ProjectDir
$Trigger3 = New-ScheduledTaskTrigger -Daily -At "08:30PM"
Register-ScheduledTask -TaskName "PredictApp_Evening_Results_2030" -Action $Action3 -Trigger $Trigger3 -Settings $Settings -Description "Predict App Evening Match Results Sync (20:30 IST)" -Force

# 4. Evening Fixtures Sync (20:35 IST)
$Action4 = New-ScheduledTaskAction -Execute $PowerShellExe -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$SyncRunner`" -ActionType fixtures -Slot 20:30" -WorkingDirectory $ProjectDir
$Trigger4 = New-ScheduledTaskTrigger -Daily -At "08:35PM"
Register-ScheduledTask -TaskName "PredictApp_Evening_Fixtures_2035" -Action $Action4 -Trigger $Trigger4 -Settings $Settings -Description "Predict App Evening Next-Day Fixtures & Odds Sync (20:35 IST)" -Force

Write-Host "`nAll 4 Predict App sync tasks registered successfully with battery resilience and logging enabled!" -ForegroundColor Green
Write-Host "Logs will be recorded in: $ProjectDir\logs\auto_sync.log"
Write-Host "You can view or manage them in Task Scheduler (taskschd.msc)."
