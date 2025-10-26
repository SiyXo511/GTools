@echo off
REM GTools Docker启动脚本 (Windows)

echo Starting GTools with Docker...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed. Please install Docker first.
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM 选择运行模式
if "%1"=="prod" (
    echo Starting production environment...
    docker-compose up -d gtools-prod
    echo Production environment started at http://localhost:5000
    echo View logs: docker-compose logs -f gtools-prod
) else if "%1"=="dev" (
    echo Starting development environment...
    docker-compose up -d gtools-dev
    echo Development environment started at http://localhost:5000
    echo View logs: docker-compose logs -f gtools-dev
) else (
    echo Usage: docker-start.bat [dev^|prod]
    echo.
    echo Available modes:
    echo   dev  - Start development environment
    echo   prod - Start production environment
    exit /b 1
)

pause
