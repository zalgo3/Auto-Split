# Installing Python dependencies
$dev = If ($env:GITHUB_JOB -eq 'Build') { '' } Else { '-dev' }
pip install wheel --upgrade
pip install -r "$PSScriptRoot/requirements$dev.txt"

# Don't compile resources on the Build CI job as it'll do so in build script
If ($dev) {
  Write-Host "`n"
  & "$PSScriptRoot/compile_resources.ps1"
}
