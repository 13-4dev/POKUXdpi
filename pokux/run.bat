@echo off
setlocal

:: Check if the script is running with admin rights
:: If not, request admin rights and rerun the script
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Set the default Chrome path
set "chrome_path=C:\Program Files\Google\Chrome\Application\chrome.exe"

:: Check if Chrome exists at the default path
if not exist "%chrome_path%" (
    echo Chrome was not found at the default path: %chrome_path%
    set /p "chrome_path=Please enter the path to chrome.exe: "
)

:: Check if the provided path exists
if not exist "%chrome_path%" (
    echo Chrome was not found at the specified path: %chrome_path%
    pause
    exit /b
)

:: Launch Chrome with proxy settings
start "" "%chrome_path%" --proxy-server="http://127.0.0.1:8080"

:: Determine the directory of the batch file
set "bat_path=%~dp0"

:: Set the relative paths based on the location of the batch file
set "pokux_path=%bat_path%POKUX\base\POKUX.exe"
set "shortcut_path=%bat_path%POKUX\POKUX.lnk"

:: Create the PowerShell script to create a shortcut
set "ps_script=%temp%\CreateShortcut.ps1"
echo $WshShell = New-Object -ComObject WScript.Shell > "%ps_script%"
echo $Shortcut = $WshShell.CreateShortcut('%shortcut_path%') >> "%ps_script%"
echo $Shortcut.TargetPath = '%pokux_path%' >> "%ps_script%"
echo $Shortcut.Arguments = '--debug' >> "%ps_script%"
echo $Shortcut.IconLocation = '%pokux_path%,0' >> "%ps_script%"
echo $Shortcut.Save() >> "%ps_script%"

:: Run the PowerShell script to create the shortcut
powershell -ExecutionPolicy Bypass -File "%ps_script%"

:: Clean up the PowerShell script
del "%ps_script%"

:: Check if the shortcut was created successfully
if exist "%shortcut_path%" (
    start "" "%shortcut_path%"
) else (
    echo The specified shortcut was not created: %shortcut_path%
    pause
    exit /b
)

:: Close the batch script terminal
exit
