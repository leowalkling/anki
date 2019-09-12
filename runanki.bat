@echo off
call activate anki
set PYTHONPATH=%PYTHONPATH%;%~dp0
python -m runanki
pause