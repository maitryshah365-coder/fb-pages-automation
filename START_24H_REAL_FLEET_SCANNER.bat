@echo off
title RAJ FB PRO - 24/7 Autonomous 24-Hour Real Fleet Scanner
cd /d "E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
set "PATH=C:\Users\Win\AppData\Local\Python\bin;%PATH%"

echo =========================================================================
echo  👑 RAJ FB PRO - AUTONOMOUS REAL-TIME 24-HOUR FLEET SCANNER
echo =========================================================================
echo  1. Scans Every Page (Followers, Fan Count, Token Health) via Meta API
echo  2. Scans Every Video Reel (Exact Views, Likes, Comments) via Batch API
echo  3. Scans Every Google Drive Folder (Exact Video Stock) via Drive API
echo  4. Updates and Syncs Dashboard Data Automatically Every 24 Hours
echo =========================================================================
echo.

python scripts/autonomous_24h_fleet_scanner.py --daemon
pause
