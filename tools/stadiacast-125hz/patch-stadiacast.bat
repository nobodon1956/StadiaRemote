@echo off
chcp 65001 >nul
setlocal
set "PS1=%~dp0patch-stadiacast.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %*
if errorlevel 1 (
    echo.
    echo Patch failed. See the error message above.
    pause
    exit /b 1
)
echo.
echo Done. You can now start stadiacast.exe (125 Hz Wi-Fi mode enabled).
pause
