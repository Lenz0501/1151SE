@echo off
set "ServiceName=postgresql-x64-18"

:: Check for admin rights using PowerShell
>nul 2>&1 net session
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Your elevated commands go below
::echo Running as administrator!

for /F "tokens=3 delims=: " %%H in ('sc query "%ServiceName%" ^| findstr "STATE"') do (
    if /I "%%H"=="RUNNING" (
        echo Service "%ServiceName%" is running. Try to STOP it...
		net stop %ServiceName%
    ) else (
        echo Service "%ServiceName%" is NOT running. Try to START it...
		net start %ServiceName%
    )
)

timeout /t 2