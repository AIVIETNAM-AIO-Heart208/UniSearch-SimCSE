@echo off
REM Tai hien SimCSE: R1 mac dinh; truyen R2 hoac R3 de chay thi nghiem khac.
REM Can Python 3.9-3.11. Ket qua luu o experiments\reproduction\results\<EXP>\
setlocal
chcp 65001 >nul
cd /d "%~dp0..\.."
set "EXP=%~1"
if "%EXP%"=="" set "EXP=R1"
set "PY311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%PY311%" (
  "%PY311%" experiments\reproduction\run_r1.py --exp %EXP%
) else (
  py -3.11 experiments\reproduction\run_r1.py --exp %EXP%
)
echo.
echo Ket qua: %CD%\experiments\reproduction\results\%EXP%\
pause
