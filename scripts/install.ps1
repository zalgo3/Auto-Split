$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }

pip install wheel --upgrade
If ($IsWindows) {
  pip install -r "$PSScriptRoot/requirements$dev-win32.txt"
}
ElseIf ($IsLinux) {
  # Required for splash screen
  sudo apt-get install python3-tk
  # Helps ensure the CI machine has the required libraries for PyQt6.
  # Not everything here is required, but using the documentation from
  # https://wiki.qt.io/Building_Qt_5_from_Git#Libxcb
  sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
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
