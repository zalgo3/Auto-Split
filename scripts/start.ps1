param ([string]$p1)
& "$PSScriptRoot/compile_resources.ps1"
If ($IsWindows) {
  python "$PSScriptRoot/../src/AutoSplit.py" $p1
}
Else {
  python3 "$PSScriptRoot/../src/AutoSplit.py" $p1
}
