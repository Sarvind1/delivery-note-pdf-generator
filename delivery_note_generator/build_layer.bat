@echo off
REM Build Lambda Layer for WeasyPrint PDF Generator (Windows)
REM NOTE: WeasyPrint requires system libraries. This script attempts a basic build.
REM For production, consider building on Amazon Linux 2 or using Docker.

echo Building Lambda Layer for WeasyPrint...

REM Create directory structure
if exist python rmdir /s /q python
mkdir python\lib\python3.11\site-packages

REM Install dependencies
pip install -r requirements.txt -t python/lib/python3.11/site-packages --platform manylinux2014_x86_64 --only-binary=:all:

REM Check if WeasyPrint installed successfully
if not exist "python\lib\python3.11\site-packages\weasyprint" (
    echo ERROR: WeasyPrint installation failed
    echo WeasyPrint requires system libraries (cairo, pango, gdk-pixbuf^)
    echo.
    echo Options:
    echo 1. Build on Amazon Linux 2 EC2 instance
    echo 2. Use Docker with amazonlinux:2 image
    echo 3. Try installing system libraries locally and rebuild
    exit /b 1
)

REM Create zip file
echo Creating lambda-layer.zip...
if exist lambda-layer.zip del lambda-layer.zip
powershell Compress-Archive -Path python -DestinationPath lambda-layer.zip -Force

REM Check file exists
if not exist lambda-layer.zip (
    echo ERROR: Failed to create lambda-layer.zip
    exit /b 1
)

echo.
echo Lambda layer created successfully: lambda-layer.zip
echo Next steps:
echo 1. Upload to AWS Lambda as a layer
echo 2. Attach layer to your Lambda function
echo 3. Upload lambda_function.py and pdf_generator_weasyprint_lambda.py
echo.
echo Note: If WeasyPrint fails in Lambda, you may need to:
echo - Build on Amazon Linux 2
echo - Include system library binaries in the layer
echo - Use a pre-built WeasyPrint layer from the community

REM Cleanup
rmdir /s /q python

pause
