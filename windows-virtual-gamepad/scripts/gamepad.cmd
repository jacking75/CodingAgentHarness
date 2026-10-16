@echo off
if defined VGAMEPAD_PYTHON goto custom
if exist "%~dp0..\.venv\Scripts\python.exe" goto bundled
echo Run scripts\setup.ps1 -Action environment first, or set VGAMEPAD_PYTHON. 1>&2
exit /b 1
:custom
"%VGAMEPAD_PYTHON%" -E "%~dp0gamepad_control.py" %*
exit /b %errorlevel%
:bundled
"%~dp0..\.venv\Scripts\python.exe" -E "%~dp0gamepad_control.py" %*
exit /b %errorlevel%
