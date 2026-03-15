@echo off
title V4 SOVEREIGN MAGIC - INTERACTIVE PURGE
echo ==========================================
echo    V4 SOVEREIGN MAGIC - PURGE PROTOCOL
echo ==========================================
echo.
echo 🛡️  Starting Sovereign Purge Menu...
echo.

:: Execute the interactive purge logic directly
python CODE\vault_sync.py --purge

echo.
echo ==========================================
echo    SESSION COMPLETE
echo ==========================================
echo.
pause
