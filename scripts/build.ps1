& "$PSScriptRoot/compile_resources.ps1"
pyinstaller `
  --windowed `
  --onedir `
  --additional-hooks-dir=Pyinstaller/hooks `
  --hidden-import pynput.keyboard._xorg `
  --hidden-import pynput.mouse._xorg `
  --icon=res/icon.ico `
  --splash=res/splash.png `
  "$PSScriptRoot/../src/AutoSplit.py"

If ($IsLinux) {
  Move-Item -Force $PSScriptRoot/../dist/AutoSplit $PSScriptRoot/../dist/AutoSplit.elf
  If ($?) {
    Write-Host 'Added .elf extension'
  }
  chmod +x $PSScriptRoot/../dist/AutoSplit.elf
  Write-Host 'Added execute permission'
}
