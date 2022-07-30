# Installing Python dependencies
$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
# Ensures installation tools are up to date.
python3 -m pip install wheel pip setuptools --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt"

# Alias python to python3 on windows
If ($IsWindows) {
  $python = (Get-Command python).Source
  $python3 = "$((Get-Item $python).Directory.FullName)/python3.exe"
  New-Item -ItemType SymbolicLink -Path $python3 -Target $python -ErrorAction SilentlyContinue
}

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  & "$PSScriptRoot/compile_resources.ps1"
}
