param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("results", "fixtures")]
    [string]$ActionType,

    [Parameter(Mandatory=$true)]
    [ValidateSet("06:30", "20:30")]
    [string]$Slot
)

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectDir = (Get-Item $PSScriptRoot\..).FullName
$LogsDir = Join-Path $ProjectDir "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}
$LogFile = Join-Path $LogsDir "auto_sync.log"
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$ManagePy = Join-Path $ProjectDir "manage.py"

$Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
"========================================================" | Out-File -FilePath $LogFile -Append -Encoding utf8
"[$Timestamp] Starting Sync: Action=$ActionType, Slot=$Slot" | Out-File -FilePath $LogFile -Append -Encoding utf8

try {
    if ($ActionType -eq "results") {
        & $VenvPython $ManagePy sync_external_matches --results --slot $Slot 2>&1 | Out-File -FilePath $LogFile -Append -Encoding utf8
    } elseif ($ActionType -eq "fixtures") {
        & $VenvPython $ManagePy sync_external_matches --fixtures --new-day-only --slot $Slot 2>&1 | Out-File -FilePath $LogFile -Append -Encoding utf8
    }
    $ExitCode = $LASTEXITCODE
} catch {
    $ExitCode = 1
    "[$Timestamp] Error executing sync: $_" | Out-File -FilePath $LogFile -Append -Encoding utf8
}

$EndTimestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
"[$EndTimestamp] Completed Sync: Action=$ActionType, Slot=$Slot (ExitCode=$ExitCode)`n" | Out-File -FilePath $LogFile -Append -Encoding utf8
exit $ExitCode
