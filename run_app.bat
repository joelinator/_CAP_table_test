Here is the equivalent of the provided bash script, rewritten for Windows users using a batch (`.bat`) file.

```bat
@echo off
setlocal enabledelayedexpansion

:: This script automates the setup and execution of the Cap Table Management Backend
:: for local testing on Windows.

:: --- Configuration ---
set "PROJECT_DIR=."
set "VENV_DIR=venv"
set "DB_NAME=captable_db"
set "REQUIREMENTS_FILE=requirements.txt"
set "ENV_FILE=.env"
set "ENV_EXAMPLE_FILE=.env.example"

:: --- Functions ---
:print_status
echo --- %1 ---
goto :eof

:: --- Main Script ---
call :print_status "Starting Cap Table Backend setup script"

:: Check for required tools
where python3 >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: python3 is not installed. Please install it to proceed.
    exit /b 1
)

where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: psql is not installed. Please ensure PostgreSQL is installed and in your PATH.
    exit /b 1
)

if not exist "%PROJECT_DIR%" (
    echo Error: Project directory not found. Please run this script from the root of the project.
    exit /b 1
)

cd "%PROJECT_DIR%"

:: 1. Setup Virtual Environment
if not exist "%VENV_DIR%" (
    call :print_status "Creating virtual environment..."
    python3 -m venv "%VENV_DIR%"
)

call :print_status "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"

:: 2. Install Dependencies
if exist "%REQUIREMENTS_FILE%" (
    call :print_status "Installing Python dependencies..."
    pip install -r "%REQUIREMENTS_FILE%"
    pip install python-dotenv
) else (
    echo Error: %REQUIREMENTS_FILE% not found. Cannot install dependencies.
    exit /b 1
)

:: 3. Setup Environment Variables
if not exist "%ENV_FILE%" (
    call :print_status "Creating a .env file from .env.example..."
    if exist "%ENV_EXAMPLE_FILE%" (
        copy "%ENV_EXAMPLE_FILE%" "%ENV_FILE%"
        echo A new .env file has been created. Please edit it with your database credentials and JWT secret.
    ) else (
        echo Error: %ENV_EXAMPLE_FILE% not found. Cannot create environment file.
        exit /b 1
    )
)

:: Load database credentials from .env and create DATABASE_URL
call :print_status "Constructing DATABASE_URL from .env variables..."
set "DB_USER="
set "DB_PASSWORD="
set "DB_NAME="
set "DB_HOST=localhost"

for /f "tokens=1,2 delims==" %%a in ('type "%ENV_FILE%" ^| findstr /v "^#" ^| findstr /v "^\s*$"') do (
    if "%%a" == "DB_USER" set "DB_USER=%%b"
    if "%%a" == "DB_PASSWORD" set "DB_PASSWORD=%%b"
    if "%%a" == "DB_NAME" set "DB_NAME=%%b"
    if "%%a" == "DB_HOST" set "DB_HOST=%%b"
)

:: Remove surrounding quotes if they exist
set "DB_USER=!DB_USER:"=!"
set "DB_PASSWORD=!DB_PASSWORD:"=!"
set "DB_NAME=!DB_NAME:"=!"
set "DB_HOST=!DB_HOST:"=!"

if defined DB_USER if defined DB_PASSWORD if defined DB_NAME (
    set "DATABASE_URL=postgresql://%DB_USER%:%DB_PASSWORD%@%DB_HOST%/%DB_NAME%"
    call :print_status "DATABASE_URL environment variable set."
) else (
    echo Warning: DB_USER, DB_PASSWORD, or DB_NAME not found in .env. DATABASE_URL not set.
)

:: 4. Create PostgreSQL Database
call :print_status "Attempting to create PostgreSQL database: %DB_NAME%"
psql -c "CREATE DATABASE %DB_NAME%" >nul 2>nul
if %errorlevel% neq 0 (
    echo Note: Database %DB_NAME% may already exist.
)

:: 5. Reminder for Redis
call :print_status "Setup complete. Remember to ensure your Redis server is running!"

:: 6. Run the Application using uvicorn with dotenv
call :print_status "Starting the FastAPI application with uvicorn..."
call :print_status "API available at http://localhost:8000"
call :print_status "API docs at http://localhost:8000/docs"
call :print_status "Use 'Ctrl+C' to stop the server."
call :print_status "Seeded credentials: Admin (admin/adminpass), Shareholder (shareholder1/shpass)."

dotenv run -- uvicorn app.main:app --host "0.0.0.0" --port 8000 --workers 4

endlocal
```
