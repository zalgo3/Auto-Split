cd "%~dp0.."
md .\src\gen
pyuic6 ".\res\about.ui" -o ".\src\gen\about.py"
pyuic6 ".\res\design.ui" -o ".\src\gen\design.py"
pyuic6 ".\res\update_checker.ui" -o ".\src\gen\update_checker.py"
pyside6-rcc ".\res\resources.qrc" -o ".\src\gen\resources_rc.py"
