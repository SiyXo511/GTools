# GTools 外网访问部署指南

本文档提供多种方式让你的GTools应用通过外网访问。

## 目录

1. [内网穿透方案](#1-内网穿透方案)
2. [云服务器部署](#2-云服务器部署)
3. [云平台托管](#3-云平台托管)
4. [路由器端口映射](#4-路由器端口映射)

---

## 1. 内网穿透方案

### 1.1 使用 ngrok（最简单，适合测试）

#### 安装ngrok
```bash
# 下载ngrok（访问 https://ngrok.com/download）
# 或使用chocolatey安装
choco install ngrok
```

#### 启动你的应用
```bash
# 本地启动应用（端口5000）
python app.py
```

#### 启动ngrok
```bash
# 创建隧道
ngrok http 5000
```

你会得到一个公网URL，例如：
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

#### 使用方式
- 访问：`https://abc123.ngrok.io`
- 免费版限制：每次重启URL会变化，有流量限制

---

### 1.2 使用 Cloudflare Tunnel（免费、稳定）

#### 安装
```bash
# 下载cloudflared
# 访问 https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Windows
choco install cloudflared
```

#### 使用
```bash
# 1. 启动你的应用
python app.py

# 2. 创建隧道
cloudflared tunnel --url http://localhost:5000
```

你会得到一个永久的URL（需要登录Cloudflare账号）。

---

### 1.3 使用 frp（开源、功能强大）

#### 服务端配置（需有公网IP的服务器）

1. 下载frp：
```bash
# 访问 https://github.com/fatedier/frp/releases
# 下载 frp_x.x.x_windows_amd64.zip
```

2. 解压后编辑 `frps.ini`（服务端）：
```ini
[common]
bind_port = 7000
token = your_secure_token
```

3. 启动服务端：
```bash
frps -c frps.ini
```

#### 客户端配置（你的电脑）

1. 编辑 `frpc.ini`：
```ini
[common]
server_addr = your_server_ip
server_port = 7000
token = your_secure_token

[gtools]
type = tcp
local_ip = 127.0.0.1
local_port = 5000
remote_port = 6000
```

2. 启动客户端：
```bash
frpc -c frpc.ini
```

3. 访问：`http://your_server_ip:6000`

---

## 2. 云服务器部署

### 2.1 使用 Docker 部署（推荐）

#### 购买云服务器
推荐平台：
- 阿里云 ECS
- 腾讯云 CVM
- 华为云 ECS
- AWS EC2
- Vultr / DigitalOcean

#### 服务器配置
- 系统：Ubuntu 22.04 LTS 或 CentOS 7+
- 配置：1核2G内存起步
- 开通端口：5000（或自定义）

#### 部署步骤

**1. 连接到服务器**
```bash
ssh root@your_server_ip
```

**2. 安装 Docker**
```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
pip install docker-compose
```

**3. 克隆项目**
```bash
git clone https://github.com/SiyXo511/GTools.git
cd GTools
```

**4. 启动服务**
```bash
# 生产环境
docker-compose up -d gtools-prod

# 查看日志
docker-compose logs -f gtools-prod
```

**5. 配置防火墙**
```bash
# Ubuntu/Debian
ufw allow 5000/tcp
ufw enable

# CentOS
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

**6. 访问应用**
```
http://your_server_ip:5000
```

### 2.2 使用 Nginx 反向代理（生产环境推荐）

#### 1. 安装 Nginx
```bash
# Ubuntu
apt-get update
apt-get install nginx

# CentOS
yum install nginx
```

#### 2. 配置 Nginx
编辑 `/etc/nginx/sites-available/gtools`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 增加文件上传大小限制
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 3. 启用配置
```bash
ln -s /etc/nginx/sites-available/gtools /etc/nginx/sites-enabled/
nginx -t
nginx -s reload
```

#### 4. 使用域名访问
- 购买域名（可选，约$10/年）
- 配置DNS：将域名解析到服务器IP
- 访问：`http://your-domain.com`

---

## 3. 云平台托管

### 3.1 Vercel 部署（简单、免费）

#### 前提
需要将Flask应用适配为serverless函数（需要修改代码）

#### 步骤
1. 注册Vercel账号
2. 导入GitHub仓库
3. 自动部署

### 3.2 Railway 部署（推荐）

#### 步骤
1. 注册Railway账号：https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的GTools仓库
5. 自动部署，获得URL

#### 配置
- 添加环境变量（如需要）
- 设置域名（可选）
- 配置持久存储

**优点**：
- 免费额度充足
- 自动CI/CD
- 简单的管理界面
- 支持自定义域名

### 3.3 Render 部署

#### 步骤
1. 注册Render账号：https://render.com
2. 创建 "New Web Service"
3. 连接GitHub仓库
4. 配置：
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. 部署并获取URL

---

## 4. 路由器端口映射

### 适用场景
- 有固定公网IP或动态公网IP
- 在家中或办公室局域网运行应用

### 步骤

#### 1. 获取公网IP
```bash
# 访问 http://ip.sb 或 http://ip.cip.cc
# 记录你的公网IP
```

#### 2. 配置路由器
1. 登录路由器管理界面（通常是192.168.1.1）
2. 找到 "端口映射" 或 "虚拟服务器"
3. 添加规则：
   - 外部端口：5000（或自定义，如8080）
   - 内部IP：你的电脑IP（如192.168.1.100）
   - 内部端口：5000
   - 协议：TCP
4. 保存并应用

#### 3. 启动应用
```bash
# 修改app.py，使其监听所有接口
# 在app.py中找到：
# app.run(debug=True)
# 改为：
# app.run(host='0.0.0.0', debug=True, port=5000)
```

#### 4. 访问应用
```
http://your_public_ip:5000
```

### 注意事项
- 需要配置防火墙允许5000端口
- 如果是动态IP，需要配置DDNS（动态域名）
- 注意安全，建议添加认证

---

## 推荐方案对比

| 方案 | 难度 | 成本 | 稳定性 | 推荐场景 |
|------|------|------|--------|----------|
| ngrok | ⭐ | 免费 | ⭐⭐ | 临时测试 |
| Cloudflare Tunnel | ⭐⭐ | 免费 | ⭐⭐⭐⭐ | 长期测试 |
| 云服务器+Docker | ⭐⭐⭐ | $5-20/月 | ⭐⭐⭐⭐⭐ | 生产环境 |
| Railway | ⭐⭐ | 免费-付费 | ⭐⭐⭐⭐⭐ | 快速部署 |
| Render | ⭐⭐ | 免费-付费 | ⭐⭐⭐⭐ | 快速部署 |
| 路由器映射 | ⭐⭐⭐ | 免费 | ⭐⭐⭐ | 家庭/办公室 |

---

## 快速开始推荐

### 测试环境（5分钟）
1. 启动应用：`python app.py`
2. 运行：`ngrok http 5000`
3. 访问提供的URL

### 生产环境（推荐）
1. 使用Railway或Render托管
2. 连接GitHub仓库自动部署
3. 绑定自定义域名（可选）

---

## 安全建议

1. **使用HTTPS**：
   - 使用Nginx + Let's Encrypt免费SSL证书
   - 或使用Cloudflare提供的HTTPS

2. **添加认证**（可选）：
   - 在app.py中添加Flask-Login
   - 或使用Basic Auth

3. **限制访问**：
   - 配置防火墙白名单
   - 使用VPN访问

4. **定期更新**：
   - 保持依赖更新
   - 关注安全补丁

---

## 故障排除

### 无法访问
1. 检查防火墙设置
2. 检查端口是否被占用
3. 检查应用是否正在运行

### 性能问题
1. 使用Gunicorn多进程
2. 配置Nginx负载均衡
3. 使用Redis缓存

---

需要更详细的某一种方案？告诉我你想使用的方案！
