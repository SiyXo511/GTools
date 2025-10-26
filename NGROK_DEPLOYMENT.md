# GTools 使用 ngrok 内网穿透部署

本指南介绍如何使用 ngrok 让 GTools 在本地访问的同时支持外网访问。

## 📋 前置要求

1. Python 3.8+ 已安装
2. ngrok 已安装
3. GTools 项目依赖已安装

## 🚀 快速开始

### 1. 安装 ngrok

#### Windows (使用Chocolatey)
```bash
choco install ngrok
```

#### Windows (手动安装)
1. 访问 https://ngrok.com/download
2. 下载 Windows 版本
3. 解压到任意目录（如 `C:\ngrok`）
4. 将路径添加到系统环境变量 PATH

#### macOS
```bash
brew install ngrok
# 或
brew install --cask ngrok
```

#### Linux
```bash
# 使用包管理器
sudo apt-get install ngrok  # Ubuntu/Debian
sudo yum install ngrok      # CentOS/RHEL

# 或手动安装
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
```

### 2. 启动 GTools 应用

```bash
# 进入项目目录
cd GTools

# 激活虚拟环境（如果有）
# Windows
.gtools_venv\Scripts\activate
# macOS/Linux
source .gtools_venv/bin/activate

# 启动应用
python app.py
```

应用启动后，会显示：
```
* Running on http://127.0.0.1:5000
```

### 3. 启动 ngrok

打开**新的终端窗口**，运行：

```bash
ngrok http 5000
```

你会看到类似的输出：
```
Session Status                online
Account                       YourAccount (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 4. 访问应用

**本地访问**：http://localhost:5000
**外网访问**：使用 ngrok 提供的 HTTPS URL（如：https://abc123.ngrok.io）

## 🔧 高级配置

### 使用固定域名（需要注册ngrok账号）

1. 注册 ngrok 账号：https://dashboard.ngrok.com/signup
2. 获取 Auth Token：https://dashboard.ngrok.com/get-started/your-authtoken
3. 配置 token：
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```
4. 启动时指定域名：
```bash
ngrok http 5000 --domain=your-chosen-domain.ngrok.io
```

### 使用配置文件

创建 `ngrok.yml` 文件：
```yaml
version: "2"
authtoken: YOUR_AUTH_TOKEN
tunnels:
  gtools:
    addr: 5000
    proto: http
    subdomain: gtools  # 自定义子域名
```

启动：
```bash
ngrok start gtools
```

### 监控访问

ngrok 提供了 Web 界面查看请求：
- 访问：http://localhost:4040
- 可以查看实时请求、响应、重放请求

## 📝 注意事项

### 免费版限制

- URL 每次启动都会变化（除非使用固定域名）
- 有连接时间限制
- 有请求数量限制
- 会显示 ngrok 品牌页面

### 付费版优势

- 固定域名
- 无连接时间限制
- 更高并发
- 无品牌页面
- 自定义域名

### 安全建议

1. **不要在公网环境泄露 URL**
2. **定期更换域名**（免费版）
3. **设置访问密码**（可选）
4. **限制文件上传大小**

### 性能优化

1. 使用 Gunicorn（生产环境）
2. 配置缓存
3. 限制并发连接

## 🐛 故障排除

### ngrok 无法连接

**问题**：`ERR_NGROK_3200`
**解决**：检查防火墙或使用 `ngrok http 5000 --region ap` 指定区域

### 端口被占用

**问题**：5000端口已被占用
**解决**：
```bash
# Windows 查看端口占用
netstat -ano | findstr :5000

# 修改应用端口
python app.py  # 修改 app.py 中的端口号
```

### 连接超时

**问题**：外网访问超时
**解决**：
- 检查本地网络
- 更换 ngrok 区域
- 使用付费账号

## 📱 使用场景

### 1. 开发测试
- 在本地开发，通过 ngrok 让远程同事访问
- 测试 API 接口
- 演示功能

### 2. Webhook 接收
- 接收 GitHub Webhook
- 接收第三方服务回调

### 3. 临时部署
- 快速向客户演示
- 短期项目展示

## 🔄 其他 ngrok 替代方案

### Cloudflare Tunnel（免费）
```bash
# 安装
choco install cloudflared

# 使用
cloudflared tunnel --url http://localhost:5000
```

### frp（开源）
- 需要自有服务器
- 完全控制
- 无流量限制

### localtunnel
```bash
npm install -g localtunnel
lt --port 5000
```

## 📊 对比表格

| 特性 | ngrok 免费 | ngrok 付费 | Cloudflare | localtunnel |
|------|-----------|-----------|------------|-------------|
| 费用 | 免费 | $8/月 | 免费 | 免费 |
| 固定域名 | ❌ | ✅ | ✅ | ❌ |
| 稳定性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 配置难度 | ⭐ | ⭐ | ⭐⭐ | ⭐ |
| 品牌页面 | ✅ | ❌ | ❌ | ✅ |

## 💡 提示

- 开发环境推荐使用 ngrok 免费版
- 需要固定域名时考虑付费或 Cloudflare
- 生产环境建议使用云服务器部署
- 重要项目不要依赖免费内网穿透

## 📚 相关资源

- [ngrok 官方文档](https://ngrok.com/docs)
- [ngrok 仪表板](https://dashboard.ngrok.com)
- [GTools GitHub](https://github.com/SiyXo511/GTools)

## ✅ 快速检查清单

- [ ] ngrok 已安装
- [ ] Python 虚拟环境已激活
- [ ] 依赖已安装（pip install -r requirements.txt）
- [ ] 应用在 localhost:5000 运行
- [ ] ngrok 隧道已启动
- [ ] 可以通过公网 URL 访问

现在你已经准备好让 GTools 通过外网访问了！🎉
