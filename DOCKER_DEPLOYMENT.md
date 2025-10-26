# Docker部署指南

本文档详细说明如何使用Docker部署GTools项目。

## 目录

- [快速开始](#快速开始)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [高级配置](#高级配置)
- [常见问题](#常见问题)

## 快速开始

### 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### 快速启动（开发环境）

```bash
# 1. 克隆项目
git clone https://github.com/SiyXo511/GTools.git
cd GTools

# 2. 启动开发环境
docker-compose up gtools-dev

# 3. 访问应用
# 打开浏览器访问 http://localhost:5000
```

### 快速启动（生产环境）

```bash
# 使用生产配置启动
docker-compose up gtools-prod

# 后台运行
docker-compose up -d gtools-prod
```

## 开发环境部署

开发环境使用Flask内置服务器，支持热重载和调试模式。

### 启动方式

#### 方式一：使用docker-compose
```bash
# 启动开发环境
docker-compose up gtools-dev

# 后台运行
docker-compose up -d gtools-dev

# 查看日志
docker-compose logs -f gtools-dev

# 停止
docker-compose down
```

#### 方式二：手动构建和运行
```bash
# 构建镜像
docker build -t gtools:dev -f Dockerfile .

# 运行容器
docker run -d \
  --name gtools-dev \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/generated_files:/app/generated_files \
  gtools:dev

# 查看日志
docker logs -f gtools-dev
```

## 生产环境部署

生产环境使用Gunicorn作为WSGI服务器，支持多工作进程。

### 启动方式

```bash
# 使用docker-compose启动生产环境
docker-compose up -d gtools-prod

# 手动构建和运行
docker build -t gtools:prod -f Dockerfile.production .

docker run -d \
  --name gtools-prod \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/generated_files:/app/generated_files \
  -e FLASK_ENV=production \
  gtools:prod
```

### Gunicorn配置

默认配置：
- Workers: 4
- Timeout: 120秒
- Bind: 0.0.0.0:5000
- 日志输出到stdout/stderr

如需自定义配置，可以修改 `Dockerfile.production` 中的CMD指令。

### 性能优化建议

1. **调整worker数量**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "app:app"]
```
Worker数量 = (2 x CPU核心数) + 1

2. **增加超时时间**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]
```

3. **配置最大请求数**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--max-requests", "1000", "app:app"]
```

## 高级配置

### 1. 使用环境变量配置

创建 `.env` 文件：
```env
FLASK_ENV=production
FLASK_DEBUG=False
UPLOAD_FOLDER=./uploads
GENERATED_FOLDER=./generated_files
MAX_UPLOAD_SIZE=100M
```

修改 `docker-compose.yml` 以加载环境变量：
```yaml
services:
  gtools-prod:
    build:
      context: .
      dockerfile: Dockerfile.production
    env_file:
      - .env
```

### 2. 配置Nginx反向代理

创建 `nginx.conf`：
```nginx
upstream gtools {
    server gtools-prod:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://gtools;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

更新 `docker-compose.yml` 添加Nginx服务：
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - gtools-prod
```

### 3. 配置健康检查

修改 `docker-compose.yml` 添加健康检查：
```yaml
services:
  gtools-prod:
    build:
      context: .
      dockerfile: Dockerfile.production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 4. 配置资源限制

```yaml
services:
  gtools-prod:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 5. 配置日志收集

#### 使用日志驱动
```yaml
services:
  gtools-prod:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :5000  # Windows
lsof -i :5000                # Linux/Mac

# 修改端口映射
docker run -p 5001:5000 gtools
```

### 2. 文件权限问题

```bash
# 设置正确的文件权限
chmod -R 755 uploads generated_files

# 或在容器内部修复
docker exec -it gtools-prod chmod -R 755 /app/uploads /app/generated_files
```

### 3. 容器无法访问

```bash
# 检查容器状态
docker ps -a

# 检查容器日志
docker logs gtools-prod

# 进入容器检查
docker exec -it gtools-prod bash
```

### 4. 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build gtools-prod

# 重启服务
docker-compose up -d --force-recreate gtools-prod
```

### 5. 备份数据

```bash
# 备份uploads目录
docker exec gtools-prod tar -czf /tmp/uploads_backup.tar.gz /app/uploads

# 复制备份文件
docker cp gtools-prod:/tmp/uploads_backup.tar.gz ./backup/

# 恢复数据
docker cp ./backup/uploads_backup.tar.gz gtools-prod:/tmp/
docker exec gtools-prod tar -xzf /tmp/uploads_backup.tar.gz -C /app/
```

## 监控和日志

### 查看日志

```bash
# Docker Compose
docker-compose logs -f gtools-prod

# Docker命令
docker logs -f gtools-prod

# 查看最近100行
docker logs --tail 100 gtools-prod
```

### 监控资源使用

```bash
# 查看资源使用情况
docker stats gtools-prod

# 查看容器详细信息
docker inspect gtools-prod
```

## 安全建议

1. **不要在生产环境使用debug模式**
2. **使用HTTPS**（通过Nginx或其他反向代理）
3. **限制文件上传大小**
4. **定期更新依赖**
5. **使用非root用户运行容器**
6. **配置防火墙规则**

## 故障排除

如果遇到问题，请检查：
1. 容器是否正在运行（`docker ps`）
2. 日志是否有错误信息（`docker logs`）
3. 端口是否映射正确
4. 文件挂载是否正确
5. 环境变量是否配置正确

## 更多信息

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Flask部署文档](https://flask.palletsprojects.com/en/3.0.x/deploying/)
