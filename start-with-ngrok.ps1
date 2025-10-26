# GTools 自动启动脚本（带ngrok）- PowerShell版本
# 功能：自动检查并安装ngrok，启动应用和隧道

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   GTools - Excel & CSV Toolkit" -ForegroundColor Cyan
Write-Host "   Auto Start with ngrok" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] Python未安装" -ForegroundColor Red
    Write-Host "请先安装Python 3.8+" -ForegroundColor Red
    Read-Host "按Enter退出"
    exit 1
}

# 检查ngrok
try {
    $ngrokVersion = ngrok version 2>&1
    Write-Host "[✓] ngrok已安装" -ForegroundColor Green
} catch {
    Write-Host "[信息] ngrok未安装，正在安装..." -ForegroundColor Yellow
    
    # 检查winget
    try {
        $wingetVersion = winget --version 2>&1
        Write-Host "[信息] 使用winget安装ngrok..." -ForegroundColor Yellow
        winget install --id ngrok.ngrok --silent --accept-package-agreements --accept-source-agreements
        Write-Host "[✓] ngrok安装成功" -ForegroundColor Green
        
        # 等待ngrok安装完成
        Start-Sleep -Seconds 3
        
        Write-Host ""
        Write-Host "==============================================" -ForegroundColor Cyan
        Write-Host "   首次运行需要配置ngrok" -ForegroundColor Cyan
        Write-Host "==============================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请在 https://ngrok.com 注册免费账号" -ForegroundColor Yellow
        Write-Host "获取你的Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
        Write-Host ""
        
        $authToken = Read-Host "请输入你的ngrok Authtoken"
        
        if ($authToken) {
            ngrok config add-authtoken $authToken
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[✓] ngrok配置完成" -ForegroundColor Green
            } else {
                Write-Host "[错误] Authtoken配置失败" -ForegroundColor Red
                Write-Host "请稍后手动运行: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "[错误] winget未安装或ngrok安装失败" -ForegroundColor Red
        Write-Host "请手动安装ngrok: https://ngrok.com/download" -ForegroundColor Yellow
        Read-Host "按Enter退出"
        exit 1
    }
}

Write-Host ""

# 检查虚拟环境
if (Test-Path ".gtools_venv\Scripts\Activate.ps1") {
    Write-Host "[信息] 激活虚拟环境..." -ForegroundColor Yellow
    & ".gtools_venv\Scripts\Activate.ps1"
} else {
    Write-Host "[警告] 未找到虚拟环境，使用系统Python" -ForegroundColor Yellow
}

# 检查依赖
Write-Host "[信息] 检查依赖..." -ForegroundColor Yellow
$flaskInstalled = python -m pip show Flask 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[信息] 正在安装依赖..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
        Read-Host "按Enter退出"
        exit 1
    }
}

Write-Host "[✓] 依赖检查完成" -ForegroundColor Green
Write-Host ""

# 显示启动信息
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   正在启动 GTools..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[信息] 应用将在: http://localhost:5000 启动" -ForegroundColor Yellow
Write-Host "[信息] ngrok隧道将自动创建" -ForegroundColor Yellow
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动Flask应用
Write-Host "[信息] 启动Flask应用..." -ForegroundColor Yellow
$flaskJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python app.py
}

# 等待应用启动
Write-Host "[信息] 等待应用启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动ngrok
Write-Host "[信息] 启动ngrok隧道..." -ForegroundColor Yellow
Start-Process ngrok -ArgumentList "http 5000" -WindowStyle Normal

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   启动完成！" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[✓] Flask应用: http://localhost:5000" -ForegroundColor Green
Write-Host "[✓] ngrok隧道: 已在新窗口启动" -ForegroundColor Green
Write-Host ""
Write-Host "请查看ngrok窗口获取公网URL" -ForegroundColor Yellow
Write-Host "按Ctrl+C停止所有服务" -ForegroundColor Yellow
Write-Host ""

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # 清理
    Write-Host ""
    Write-Host "[信息] 正在停止服务..." -ForegroundColor Yellow
    Stop-Job $flaskJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob -ErrorAction SilentlyContinue
    Write-Host "[✓] 服务已停止" -ForegroundColor Green
}
