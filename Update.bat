@echo off

python --version 3>NUL
if errorlevel 1 goto errorNoPython

python update.py
goto:eof

:errorNoPython
echo Error^: Python not installed