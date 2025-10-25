# GTools - Excel & CSV Toolkit

一个基于Flask的Web工具集，用于处理Excel和CSV文件的数据转换操作。

## 功能特性

### 🔄 数据转换工具

1. **列转列表** - 将Excel/CSV文件的指定列转换为列表格式
2. **列转JSON** - 将Excel/CSV文件的指定列转换为JSON格式
3. **JSON转表格** - 将JSON数据转换为CSV/Excel表格
4. **剪贴板处理** - 直接处理剪贴板数据，支持列表和JSON转换

### 📁 支持的文件格式

- **输入格式**: Excel (.xlsx, .xls), CSV, JSON
- **输出格式**: CSV, Excel (.xlsx, .xls), Markdown (.md), TXT

### 🌟 主要功能

- ✅ 支持中文内容处理
- ✅ 自动处理NaN值（转换为null）
- ✅ 多种输出方式（页面显示/文件下载）
- ✅ 响应式Web界面
- ✅ 实时数据预览

## 安装和运行

### 环境要求

- Python 3.8+
- pip

### 安装步骤

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

## 项目结构

```
GTools/
├── app.py                 # Flask应用主文件
├── requirements.txt       # 项目依赖
├── .gitignore            # Git忽略文件
├── excel_processor/      # 数据处理模块
│   ├── __init__.py
│   ├── utils.py          # 工具函数
│   ├── to_list.py        # 列转列表功能
│   ├── to_json.py        # 列转JSON功能
│   ├── from_json.py      # JSON转表格功能
│   └── clipboard.py      # 剪贴板处理功能
├── templates/            # HTML模板
│   ├── index.html
│   ├── convert_list.html
│   ├── convert_json.html
│   ├── convert_from_json.html
│   └── process_clipboard.html
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

## 技术栈

- **后端**: Flask 3.0.0
- **数据处理**: pandas 2.2.2, numpy 1.26.4
- **Excel支持**: openpyxl 3.1.2, xlrd 2.0.2, xlwt 1.3.0
- **前端**: HTML5, CSS3, JavaScript (ES6+)
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
