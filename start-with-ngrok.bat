@echo off
REM GTools 自动启动脚本（带ngrok）
REM 此脚本会自动检查ngrok是否安装，并启动应用和ngrok隧道

echo ==============================================
echo    GTools - Excel ^& CSV Toolkit
echo    Auto Start with ngrok
echo ==============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或不在PATH中
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo [✓] Python已安装

REM 检查ngrok是否安装
ngrok version >nul 2>&1
if errorlevel 1 (
    echo [信息] ngrok未安装，正在安装...
    echo.
    
    REM 检查winget是否可用
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo [错误] winget未安装
        echo 请手动安装ngrok: https://ngrok.com/download
        echo 或使用以下命令安装winget: https://aka.ms/getwinget
        pause
        exit /b 1
    )
    
    echo [信息] 使用winget安装ngrok...
    winget install ngrok.ngrok
    if errorlevel 1 (
        echo [错误] ngrok安装失败
        echo 请手动从 https://ngrok.com/download 下载并安装
        pause
        exit /b 1
    )
    
    echo [✓] ngrok安装成功
    echo [信息] 配置ngrok...
    
    REM 等待ngrok安装完成
    timeout /t 2 /nobreak >nul
    
    echo.
    echo ==============================================
    echo    首次运行需要配置ngrok
    echo ==============================================
    echo.
    echo 请在 https://ngrok.com 注册免费账号
    echo 获取你的Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
    echo.
    set /p AUTHTOKEN="请输入你的ngrok Authtoken: "
    
    ngrok config add-authtoken %AUTHTOKEN%
    if errorlevel 1 (
        echo [错误] Authtoken配置失败
        echo 请稍后手动运行: ngrok config add-authtoken YOUR_TOKEN
        pause
    )
    
    echo [✓] ngrok配置完成
    echo.
) else (
    echo [✓] ngrok已安装
    echo.
)

REM 检查虚拟环境
if exist ".gtools_venv\Scripts\activate.bat" (
    echo [信息] 激活虚拟环境...
    call .gtools_venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，使用系统Python
)

REM 检查依赖
echo [信息] 检查依赖...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [信息] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [✓] 依赖检查完成
echo.

REM 显示启动信息
echo ==============================================
echo    正在启动 GTools...
echo ==============================================
echo.
echo [信息] 应用将在: http://localhost:5000 启动
echo [信息] ngrok隧道将自动创建
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动Flask应用（在后台）
start /b python app.py

REM 等待应用启动
echo [信息] 等待应用启动...
timeout /t 3 /nobreak >nul

REM 启动ngrok
echo [信息] 启动ngrok隧道...
start "GTools ngrok" cmd /k "echo ngrok隧道已启动 ^& echo. ^& echo 本地访问: http://localhost:5000 ^& echo 外网访问: 查看下面的Forwarding URL ^& echo. ^& echo 按任意键关闭ngrok ^& echo. ^& ngrok http 5000 ^& pause"

echo.
echo ==============================================
echo    启动完成！
echo ==============================================
echo.
echo [✓] Flask应用: http://localhost:5000
echo [✓] ngrok隧道: 已在新窗口启动
echo.
echo 请查看ngrok窗口获取公网URL
echo.
echo 按任意键退出...
pause >nul
