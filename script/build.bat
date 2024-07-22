@echo off

echo Checking venv dir...
REM Check if virtual environment exists. If not, create it.
if not exist .venv\ (
    python -m venv .venv
)

REM Activate the virtual environment for Windows.
call .venv\Scripts\activate.bat
echo Virtual Environment Activated"

echo Installing requirements...
REM Check if pyinstaller is installed in the virtual environment. If not, install it.
pip show pyinstaller >nul 2>&1 || pip install pyinstaller

echo Compiling...
pyinstaller main.py --onefile --console --name pyshell --add-data "LICENSE:dist/"