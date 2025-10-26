# GTools 快速启动指南

## 🚀 一键启动（推荐）

### Windows批处理脚本
双击运行 `start-with-ngrok.bat`

### Windows PowerShell
```powershell
.\start-with-ngrok.ps1
```

脚本会自动：
1. ✅ 检查Python是否安装
2. ✅ 检查ngrok是否安装（未安装则自动安装）
3. ✅ 首次运行时引导配置ngrok
4. ✅ 检查并安装依赖
5. ✅ 启动Flask应用
6. ✅ 启动ngrok隧道

## 📝 手动启动

如果你想手动启动，按照以下步骤：

### 第一步：安装ngrok（如果未安装）

#### 使用winget安装
```powershell
winget install ngrok.ngrok
```

#### 或手动安装
1. 访问 https://ngrok.com/download
2. 下载Windows版本
3. 解压并添加到PATH

### 第二步：配置ngrok（首次使用）

```powershell
# 获取你的Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 第三步：启动应用

打开**第一个终端**：
```bash
python app.py
```

打开**第二个终端**：
```bash
ngrok http 5000
```

### 第四步：访问

- **本地访问**：http://localhost:5000
- **外网访问**：使用ngrok提供的URL（如：https://abc123.ngrok.io）

## 🐛 常见问题

### ngrok未安装
```powershell
# 方法1：使用winget
winget install ngrok.ngrok

# 方法2：使用chocolatey
choco install ngrok

# 方法3：手动下载
# 访问 https://ngrok.com/download
```

### 端口5000被占用
修改 `app.py` 中的端口号，例如改为5001：
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

然后启动ngrok：
```bash
ngrok http 5001
```

### Python虚拟环境问题
```bash
# 创建虚拟环境
python -m venv .gtools_venv

# 激活虚拟环境（Windows）
.gtools_venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py
```

### ngrok Authtoken无效
1. 重新获取token：https://dashboard.ngrok.com/get-started/your-authtoken
2. 重新配置：
```bash
ngrok config add-authtoken YOUR_NEW_TOKEN
```

## 📚 更多帮助

- 详细文档：查看 [NGROK_DEPLOYMENT.md](NGROK_DEPLOYMENT.md)
- 项目主页：https://github.com/SiyXo511/GTools
- ngrok文档：https://ngrok.com/docs

## 🔧 高级配置

### 使用固定域名
需要ngrok账号（免费或付费）：
```bash
ngrok http 5000 --domain=your-chosen-domain.ngrok.io
```

### 查看实时请求
ngrok提供了Web界面：
- 访问：http://localhost:4040

### 停止服务
按 `Ctrl+C` 停止Flask应用
在ngrok窗口中按任意键停止ngrok

## ✅ 快速检查清单

- [ ] Python 3.8+ 已安装
- [ ] 已克隆项目
- [ ] 已安装依赖（`pip install -r requirements.txt`）
- [ ] ngrok已安装
- [ ] ngrok已配置（可选）
- [ ] 已阅读本文档

完成！现在你可以一键启动GTools了！🎉
