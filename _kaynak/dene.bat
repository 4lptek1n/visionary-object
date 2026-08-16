@echo off
set "KAYNAK=%~dp0"
set "VO_CIKTI=%KAYNAK%.."
cd /d "%KAYNAK%"
echo CIKTI: %VO_CIKTI%
python build_en.py
