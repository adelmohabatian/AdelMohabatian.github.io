@echo off
setlocal
cd /d "%~dp0"
echo WebSocial - carpet online editor pilot (LOCAL PREVIEW ONLY)
echo.
if not exist "releases\site.zip" (
  echo ERROR: releases\site.zip not found. Copy these files to the REPOSITORY ROOT.
  pause
  exit /b 1
)
python -c "from PIL import Image; print('Pillow ready')" >nul 2>&1
if errorlevel 1 (
  echo Pillow is needed. Run: python -m pip install Pillow
  pause
  exit /b 1
)
python tools\websocial_online_pilot_builder.py --base-zip releases\site.zip --data content\pilot\carpet.json --media-dir content\pilot\media --output preview\pilot-site.zip --include-drafts
if errorlevel 1 (
  echo Build failed. See error above.
  pause
  exit /b 1
)
echo.
echo Preview ZIP created at preview\pilot-site.zip
 echo Extract it to a SEPARATE folder, then run python -m http.server 8080 there.
pause
