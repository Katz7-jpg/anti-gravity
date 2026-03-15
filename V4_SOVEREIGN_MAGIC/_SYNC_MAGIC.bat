@echo off
title V4 SOVEREIGN MAGIC - SYNC ALL
echo ==========================================
echo    V4 SOVEREIGN MAGIC - SYNC ALL
echo ==========================================
echo.
echo [1/3] Connecting to Supabase...
python CODE\vault_sync.py --sync-all
echo.
echo [2/3] Syncing Kilo Memory Bank...
python CODE\vault_sync.py --kilo-sync
echo.
echo [3/3] Syncing OpenCode Context...
python CODE\vault_sync.py --opencode-sync
echo.
echo ==========================================
echo    SYNC COMPLETE
echo ==========================================
echo.
echo Your Kilo Extension and OpenCode are now
echo synchronized with the Sovereign Vault.
echo.
pause
