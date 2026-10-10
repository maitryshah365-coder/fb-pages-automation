@echo off
title RAJ FB PRO - Real Facebook Monetization Live Engine
cd /d "E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
set "PATH=C:\Users\Win\AppData\Local\Python\bin;%PATH%"

echo ========================================================
echo  RAJ FB PRO - REAL LIVE FACEBOOK AUDIT ENGINE
echo ========================================================
echo  Checking and launching Live Audit Server on Port 8089...
echo.

python scripts/live_audit_server.py
pause
