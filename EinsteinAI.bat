@echo off
REM Start the Einstein AI bot in GUI mode silently
REM We use powershell to launch the script with window hiding logic
powershell.exe -WindowStyle Hidden -File "EinsteinAI.ps1"
exit
