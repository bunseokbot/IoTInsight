@echo off

echo "Installing Python Library"
call pip install -r "%~dp0api\requirements.txt"
echo.
echo "Installing NodeJS Library"
call npm install
echo "Electron SQLITE3 Rebuild"
npm run rebuild
echo.