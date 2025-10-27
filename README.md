# GTools - Excel & CSV Toolkit

一个基于Flask的Web工具集，用于处理Excel和CSV文件的数据转换操作。

## 功能特性

### 🔄 数据转换工具

1. **列转列表** - 将Excel/CSV文件的指定列转换为列表格式
2. **列转JSON** - 将Excel/CSV文件的指定列转换为JSON格式
3. **JSON转表格** - 将JSON数据转换为CSV/Excel表格
4. **剪贴板处理** - 直接处理剪贴板数据，支持列表和JSON转换
5. **SQL转表格** - 将SQL INSERT语句转换为CSV/Excel/Markdown表格

### 📁 支持的文件格式

- **输入格式**: Excel (.xlsx, .xls), CSV, JSON, SQL
- **输出格式**: CSV, Excel (.xlsx, .xls), Markdown (.md), TXT

### 🌟 主要功能

- ✅ 支持中文内容处理
- ✅ 自动处理NaN值（转换为null）
- ✅ 多种输出方式（页面显示/文件下载）
- ✅ 响应式Web界面
- ✅ 实时数据预览
- ✅ Docker部署支持

## 快速开始

### 方式一：Docker部署（推荐）

#### 使用docker-compose（最简单）

```bash
# 克隆项目
git clone https://github.com/SiyXo511/GTools.git
cd GTools

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 使用Docker命令

```bash
# 构建镜像
docker build -t gtools .

# 运行容器
docker run -d \
  --name gtools \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/generated_files:/app/generated_files \
  gtools

# 查看日志
docker logs -f gtools

# 停止容器
docker stop gtools
docker rm gtools
```

### 方式二：本地部署

#### 环境要求

- Python 3.8+
- pip

#### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/SiyXo511/GTools.git
cd GTools
```

2. 创建虚拟环境
```bash
python -m venv .gtools_venv
```

3. 激活虚拟环境
```bash
# Windows
.gtools_venv\Scripts\activate

# macOS/Linux
source .gtools_venv/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 运行应用
```bash
python app.py
```

6. 访问应用
打开浏览器访问: http://127.0.0.1:5000

## Docker部署说明

### 端口配置

- 默认端口：5000
- 如需修改端口，编辑 `docker-compose.yml` 中的 `5000:5000`

### 数据持久化

项目自动挂载以下目录到宿主机：
- `./uploads` - 用户上传的文件
- `./generated_files` - 生成的文件

### 环境变量

可以通过环境变量配置应用：

```yaml
environment:
  - FLASK_ENV=production
  - FLASK_DEBUG=False
  - FLASK_HOST=0.0.0.0
  - FLASK_PORT=5000
```

### 生产环境建议

1. **使用反向代理**（如Nginx）
2. **启用HTTPS**
3. **配置日志收集**
4. **设置资源限制**

示例Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 项目结构

```
GTools/
├── app.py                 # Flask应用主文件
├── requirements.txt       # 项目依赖
├── Dockerfile            # Docker镜像配置
├── docker-compose.yml    # Docker编排配置
├── .dockerignore         # Docker忽略文件
├── .gitignore            # Git忽略文件
├── README.md             # 项目文档
├── excel_processor/      # 数据处理模块
│   ├── __init__.py
│   ├── utils.py          # 工具函数
│   ├── to_list.py        # 列转列表功能
│   ├── to_json.py        # 列转JSON功能
│   ├── from_json.py      # JSON转表格功能
│   ├── clipboard.py      # 剪贴板处理功能
│   └── sql_to_table.py   # SQL转表格功能
├── templates/            # HTML模板
│   ├── index.html
│   ├── convert_list.html
│   ├── convert_json.html
│   ├── convert_from_json.html
│   ├── process_clipboard.html
│   └── convert_sql.html
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── uploads/              # 上传文件目录
└── generated_files/      # 生成文件目录
```

## 使用说明

### 1. 列转列表
- 上传Excel/CSV文件
- 选择要转换的列
- 选择输出方式（页面显示/文件下载）

### 2. 列转JSON
- 上传Excel/CSV文件
- 选择要转换的列（支持多选）
- 选择输出方式（页面显示/文件下载/添加到表格）

### 3. JSON转表格
- 上传JSON文件
- 选择输出格式（CSV/Excel）
- 下载转换后的文件

### 4. 剪贴板处理
- 粘贴数据到文本框
- 选择转换类型（列表/JSON转表格）
- 选择输出方式和格式

### 5. SQL转表格
- 上传SQL文件（.sql或.txt）
- 选择输出格式（CSV/Excel/Markdown）
- 下载转换后的表格文件

## 技术栈

- **后端**: Flask 3.0.0
- **数据处理**: pandas 2.2.2, numpy 1.26.4
- **Excel支持**: openpyxl 3.1.2, xlrd 2.0.2, xlwt 1.3.0
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **容器化**: Docker, Docker Compose
- **样式**: 自定义CSS，响应式设计

## 开发说明

### 添加新功能

1. 在 `excel_processor/` 目录下创建新的处理模块
2. 在 `__init__.py` 中导入新函数
3. 在 `app.py` 中添加新的路由
4. 创建对应的HTML模板和JavaScript处理逻辑

### 代码规范

- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加适当的错误处理
- 编写清晰的文档字符串

## 常见问题

### Docker相关问题

**Q: 如何查看容器日志？**
```bash
docker-compose logs -f
# 或
docker logs -f gtools
```

**Q: 如何重启服务？**
```bash
docker-compose restart
# 或
docker restart gtools
```

**Q: 如何更新应用？**
```bash
git pull
docker-compose build
docker-compose up -d
```

### 性能优化

1. **增加Gunicorn**（生产环境）
```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. **使用Redis缓存**（可选）
3. **设置文件大小限制**
4. **配置请求超时**

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的Excel/CSV数据转换功能
- 支持剪贴板数据处理
- 响应式Web界面
- 支持Docker部署

### v1.1.0
- 添加Docker和Docker Compose支持
- 优化文件处理性能
- 改进错误处理机制

### v1.2.0
- 新增SQL转表格功能
- 支持将SQL INSERT语句转换为CSV/Excel/Markdown表格
- 支持复杂数据类型（JSON、字典、列表）
- 支持反引号和中文字段名
- 文件上传限制提升至50MB
- 移除剪切板SQL输入功能，简化为仅支持文件上传