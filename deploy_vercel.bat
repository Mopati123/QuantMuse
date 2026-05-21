@echo off
echo ========================================
echo QuantMuse Vercel Deployment Script
echo ========================================
echo.

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Vercel CLI
        pause
        exit /b 1
    )
)

echo Vercel CLI is installed.
echo.

REM Check if we're in the right directory
if not exist "vercel.json" (
    echo ERROR: vercel.json not found. Please run this script from the QuantMuse directory.
    pause
    exit /b 1
)

if not exist "api\index.py" (
    echo ERROR: api\index.py not found. Please run this script from the QuantMuse directory.
    pause
    exit /b 1
)

echo Found required files.
echo.

REM Check if user is logged in to Vercel
echo Checking Vercel login status...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo Not logged in to Vercel. Please login:
    vercel login
    if %errorlevel% neq 0 (
        echo ERROR: Failed to login to Vercel
        pause
        exit /b 1
    )
)

echo Logged in to Vercel.
echo.

REM Deploy to Vercel
echo Deploying to Vercel...
echo This may take a few minutes...
echo.

vercel --prod

if %errorlevel% neq 0 (
    echo ERROR: Deployment failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo Your QuantMuse Interactive Dashboard is now live on Vercel.
echo.
echo Next steps:
echo 1. Open the provided URL to test your dashboard
echo 2. Test all features and functionality
echo 3. Monitor the Vercel dashboard for any issues
echo.
echo For support, check VERCEL_DEPLOYMENT_GUIDE.md
echo.

pause
