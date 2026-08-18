@echo off
setlocal
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (where py >nul 2>nul && set "PY=py")
if not defined PY (
  echo [TerminalPet] Python 3 not found. Install it from https://www.python.org
  exit /b 1
)
%PY% "%~dp0pet.py" %*
endlocal
