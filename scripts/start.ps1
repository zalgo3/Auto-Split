param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
If ($IsLinux) {
  sudo python "$PSScriptRoot/../src/AutoSplit.py" $p1
}
Else {
  python "$PSScriptRoot/../src/AutoSplit.py" $p1
}
