@echo off
REM Initialize Simply Lawverse Database
echo.
echo =====================================
echo Simply Lawverse - Database Setup
echo =====================================
echo.

REM Activate virtual environment
call myenv\Scripts\activate.bat

REM Run the Python initialization script
echo Starting database initialization...
python init_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================
    echo SUCCESS: Database initialized!
    echo =====================================
    echo.
    echo The application is ready to run.
    echo.
) else (
    echo.
    echo =====================================
    echo ERROR: Database setup failed!
    echo =====================================
    echo.
)

pause
