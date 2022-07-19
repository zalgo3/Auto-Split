$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }

pip install wheel --upgrade
If ($IsWindows) {
  pip install -r "$PSScriptRoot/requirements$dev-win32.txt"
}
ElseIf ($IsLinux) {
  # Required for splash screen
  sudo apt-get install python3-tk libxrender-dev libxkbcommon-dev
  pip install -r "$PSScriptRoot/requirements$dev-linux.txt"
}
Else {
  pip install -r "$PSScriptRoot/requirements$dev.txt"
}

If ($dev) {
  Write-Host "`n"
  & "$PSScriptRoot/compile_resources.ps1"
}

if (-not $env:GITHUB_JOB -or $env:GITHUB_JOB -eq 'Pyright') {
  npm install -g pyright@latest
  npm list -g pyright
}
