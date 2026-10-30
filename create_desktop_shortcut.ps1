# PowerShell script to create a Desktop shortcut for Panther

$exePath    = 'C:\Users\HP\System Management Project\dist\PantherApp.exe'
$workingDir = 'C:\Users\HP\System Management Project\dist'
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop 'Panther System Intelligence.lnk'

$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $workingDir
$shortcut.Save()
Write-Host "✅ Desktop shortcut created at $shortcutPath"
