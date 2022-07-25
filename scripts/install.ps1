# Validating user groups on Linux
If ($IsLinux -and -not $env:GITHUB_JOB) {
  $groups = groups
  if ($groups.Contains('input') -and $groups.Contains('tty')) {
    Write-Host "User $Env:USER is already part of groups input and tty. No actions taken."
  }
  Else {
    # https://github.com/boppreh/keyboard/issues/312
    Write-Host "User $Env:USER isn't part of groups input and tty. It is required to install the keyboard module."
    sudo usermod -a -G 'tty,input' $Env:USER
    sudo chmod +0666 /dev/uinput
    Write-Output 'KERNEL=="uinput", TAG+="uaccess""' > /etc/udev/rules.d/50-uinput.rules
    Write-Output 'SUBSYSTEM=="input", MODE="0666" GROUP="plugdev"' > /etc/udev/rules.d/12-input.rules
    Write-Output 'SUBSYSTEM=="misc", MODE="0666" GROUP="plugdev"' >> /etc/udev/rules.d/12-input.rules
    Write-Output 'SUBSYSTEM=="tty", MODE="0666" GROUP="plugdev"' >> /etc/udev/rules.d/12-input.rules
    Write-Host 'You have been added automatically,' `
      "but still need to manually terminate your session with 'loginctl terminate-user $Env:USER'"
    Exit
  }
}

# Alias pip3 to pip
If ($IsMacOS) {
  pip3 install pip --upgrade
}

# Installing Python dependencies
$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
pip install wheel --upgrade
If ($IsLinux) {
  If (-not $env:GITHUB_JOB -or $env:GITHUB_JOB -eq 'Build') {
    # Required for splash screen
    sudo apt-get install python3-tk
    # Helps ensure build machine has the required PyQt6 libraries for all target machines.
    # Not everything here is required, but using the documentation from
    # https://wiki.qt.io/Building_Qt_5_from_Git#Libxcb
    sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
  }
}
If ($IsLinux -and $env:GITHUB_JOB) {
  # Can't set groups as above on CI, so we have to rely on root
  sudo pip install -r "$PSScriptRoot/requirements$dev.txt"
}
ElseIf ($IsMacOS) {
  # Installing keyboard from HEAD without pyobjc results in "ModuleNotFoundError: No module named 'Quartz'"
  pip install pyobjc
  pip install -r "$PSScriptRoot/requirements$dev-darwin.txt"
}
Else {
  pip install -r "$PSScriptRoot/requirements$dev.txt"
}

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  Write-Host "`n"
  & "$PSScriptRoot/compile_resources.ps1"
}

# Only the Pyright job and local devs have node installed
if (-not $env:GITHUB_JOB -or $env:GITHUB_JOB -eq 'Pyright') {
  npm install --global pyright@latest
  npm list --global pyright
}
