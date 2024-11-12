@echo off
setlocal enabledelayedexpansion

echo [%date% %time%] Starting Aider setup...

REM Check if conda is available
echo [%date% %time%] Checking if conda is available...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] Error: Conda is not installed or not in the system PATH.
    exit /b 1
)

REM Create directory if it doesn't exist
echo [%date% %time%] Checking if D:\tmp\genai\venv directory exists...
if not exist "D:\tmp\genai\venv" (
    echo [%date% %time%] Creating directory D:\tmp\genai\venv...
    mkdir "D:\tmp\genai\venv"
)

REM Check if conda environment exists
echo [%date% %time%] Checking if conda environment 'aider-conda-env' exists...
conda info --envs | findstr /C:"aider-conda-env" >nul
if %errorlevel% neq 0 (
    echo [%date% %time%] Creating conda environment 'aider-conda-env'...
    conda create --prefix "D:\tmp\genai\venv\aider-conda-env" python=3.11 -y
    echo [%date% %time%] Conda environment created. Please run this batch file again to launch aider.
) else (
    echo [%date% %time%] Conda environment 'aider-conda-env' already exists.
)

REM Activate the conda environment
echo [%date% %time%] Activating conda environment 'aider-conda-env'...
call conda activate "D:\tmp\genai\venv\aider-conda-env"

REM Install or upgrade aider
echo [%date% %time%] Installing/upgrading aider...
pip install --upgrade aider-chat

REM Copy configuration file if it doesn't exist
echo [%date% %time%] Checking if aider-config.yml exists...
if not exist "aider-config.yml" (
    echo [%date% %time%] Copying aider-config.yml...
    copy "D:\github\ai-coding-assistants\aider-fork\aider-config.yml" .
) else (
    echo [%date% %time%] aider-config.yml already exists in the current directory.
)

REM Check if .env file exists and set environment variables
echo [%date% %time%] Checking if .env file exists...
if exist ".env" (
    echo [%date% %time%] Setting environment variables from .env file...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
        echo [%date% %time%] Set: %%a
    )
) else (
    echo [%date% %time%] No .env file found in the current directory.
)

REM Launch aider
echo [%date% %time%] Launching aider...
aider --chat-mode code --config aider-config.yml

echo [%date% %time%] Aider session ended. To deactivate the conda environment, type 'conda deactivate'.
