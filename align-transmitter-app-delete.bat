@echo off
setlocal enabledelayedexpansion

REM === ADB path (portable) ===
set ADB=%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools\adb.exe

REM === Check ADB exists ===
if not exist "%ADB%" (
    echo ADB not found at:
    echo %ADB%
    pause
    exit /b
)

REM === Check device connected ===
echo Checking device...
%ADB% devices | findstr /R /C:"device$" >nul
if errorlevel 1 (
    echo No device detected. Make sure USB debugging is enabled.
    pause
    exit /b
)

echo Device connected OK
echo.

REM === Packages to remove ===
set PACKAGES=^
com.google.android.gm ^
com.google.android.keep ^
com.google.android.apps.youtube.music ^
com.google.android.apps.maps ^
com.google.android.apps.photos ^
com.google.android.googlequicksearchbox ^
com.google.android.apps.wellbeing ^
com.google.android.apps.messaging ^
com.google.android.deskclock ^
com.google.android.calculator ^
com.google.android.marvin.talkback ^
com.google.android.feedback ^
com.google.android.apps.restore ^
com.google.android.apps.safetyhub ^
com.google.android.apps.turbo ^
com.google.android.printservice.recommendation ^
com.google.android.tag ^
com.android.dreams.basic ^
com.android.dreams.phototable ^
com.android.protips ^
com.android.traceur ^
com.android.printspooler ^
com.mmbox.xbrowser ^
com.google.android.inputmethod.pinyin ^
com.google.android.contacts ^
com.google.android.apps.messaging ^
com.android.mms ^
org.codeaurora.dialer ^
com.ms.msdisplay

REM === Log file ===
set LOGFILE=debloat_log.txt
echo Debloat started > %LOGFILE%
echo ======================== >> %LOGFILE%

REM === Loop ===
for %%p in (%PACKAGES%) do (
    echo Removing %%p ...
    %ADB% shell pm uninstall --user 0 %%p >> %LOGFILE% 2>&1

    if !errorlevel! == 0 (
        echo [OK] %%p
    ) else (
        echo [FAIL] %%p (check log)
    )
)

echo.
echo Done. Log saved to %LOGFILE%
pause
