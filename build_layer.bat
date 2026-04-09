@echo off
REM Lambda Layer Build Script for PDF Generator Dependencies (Windows)
REM This script creates a Lambda layer with all required Python dependencies

echo Building Lambda Layer for PDF Generator...

REM Create layer directory structure
set LAYER_DIR=lambda-layer
set PYTHON_DIR=%LAYER_DIR%\python

REM Clean up previous builds
if exist %LAYER_DIR% rmdir /s /q %LAYER_DIR%
if exist lambda-layer.zip del lambda-layer.zip

REM Create directory structure
mkdir %PYTHON_DIR%

echo Installing dependencies...

REM Install dependencies to the python directory
pip3 install --platform manylinux2014_x86_64 --target=%PYTHON_DIR% --implementation cp --python-version 3.11 --only-binary=:all: --upgrade -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Error installing dependencies
    exit /b 1
)

echo Cleaning up unnecessary files...
cd %PYTHON_DIR%
for /d /r %%i in (tests) do @if exist "%%i" rmdir /s /q "%%i"
for /d /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i"
for /d /r %%i in (*.dist-info) do @if exist "%%i" rmdir /s /q "%%i"
for /d /r %%i in (*.egg-info) do @if exist "%%i" rmdir /s /q "%%i"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

cd ..\..

echo Creating layer zip file...
REM Using PowerShell to create zip (works on Windows 10+)
powershell -command "Compress-Archive -Path %LAYER_DIR%\* -DestinationPath lambda-layer.zip -Force"

if %ERRORLEVEL% neq 0 (
    echo Error creating zip file
    exit /b 1
)

echo.
echo Layer built successfully!
echo Layer file: lambda-layer.zip
echo.
echo Next steps:
echo 1. Upload lambda-layer.zip to AWS Lambda as a layer:
echo    aws lambda publish-layer-version ^
echo      --layer-name pdf-generator-dependencies ^
echo      --description "Dependencies for PDF generator" ^
echo      --zip-file fileb://lambda-layer.zip ^
echo      --compatible-runtimes python3.11
echo.
echo 2. Or upload via AWS Console:
echo    - Go to Lambda ^> Layers ^> Create layer
echo    - Upload lambda-layer.zip
echo    - Select compatible runtimes: Python 3.11
echo.
echo 3. Attach the layer to your Lambda function
echo.
