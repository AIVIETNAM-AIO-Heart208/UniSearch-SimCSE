@echo off
REM Reproduce R1 by default. Pass R2 or R3 to select a different experiment.
setlocal
set "PYTHONUTF8=1"
set "EXP=%~1"
if "%EXP%"=="" set "EXP=R1"
set "PY311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%PY311%" (
  "%PY311%" "%~dp0run_r1.py" --exp "%EXP%"
  goto :done
)
for %%V in (3.11 3.10 3.9) do (
  py -%%V -c "pass" >nul 2>&1
  if not errorlevel 1 (
    py -%%V "%~dp0run_r1.py" --exp "%EXP%"
    goto :done
  )
)
echo Python 3.9-3.11 is required. 1>&2
exit /b 1
:done
exit /b %errorlevel%
