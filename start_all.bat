@echo off
echo ========================================================
echo Installing Python dependencies...
echo ========================================================
pip install flask flask-cors pandas

echo.
echo ========================================================
echo Initializing fake threat database...
echo ========================================================
python init_db.py

echo.
echo ========================================================
echo Starting Python backend (Flask)...
echo ========================================================
start cmd /k "python app.py"

echo.
echo ========================================================
echo Installing Node.js dependencies for frontend...
echo ========================================================
cd frontend
call npm install react-router-dom react-countup --save
call npm install

echo.
echo ========================================================
echo Starting React frontend...
echo ========================================================
start cmd /k "npm start"

echo.
echo Both servers are starting up in new windows.
echo If you see a Windows Firewall prompt, please click "Allow Access".
pause
