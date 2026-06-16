# 档案管理分析系统

> 一个完全离线部署的OCR档案分析系统，集成员工档案管理、任务分配、自动OCR识别和AI大模型分析报告生成。

## 🎯 功能特性

- 📋 **员工档案管理** - 完整的员工信息库管理
- 📁 **档案批量上传** - 支持PDF、图片等多格式档案
- 🔍 **自动OCR识别** - 基于PaddleOCR的高精度文字识别（中文优化）
- 🤖 **AI分析报告** - 本地大模型（Llama2/Mistral）自动生成分析报告
- 👥 **任务分配** - 员工任务分配与跟踪
- 📊 **数据导出** - 支持报告导出为PDF/Excel
- 🔐 **离线运行** - 完全本地部署，数据不出网络
- 🎨 **Web管理界面** - 易用的后台管理系统

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│      Web管理系统 (OrangeHRM)        │
│   http://localhost:8080             │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼───┐  ┌──▼────────┐
│ OCR  │  │ LLM  │  │ 数据库     │
│服务  │  │服务  │  │ MySQL     │
│8001  │  │11434 │  │ 3306      │
└──────┘  └──────┘  └───────────┘
    ↓         ↓
PaddleOCR  Ollama+Llama2
```

## 📦 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **后台系统** | OrangeHRM (PHP) | 开源HR管理系统 |
| **数据库** | MySQL 5.7 | 关系型数据库 |
| **OCR识别** | PaddleOCR | 百度开源OCR引擎 |
| **大模型** | Ollama + Llama2 | 本地推理框架 |
| **OCR服务** | Python FastAPI | OCR调用API |
| **分析服务** | Python FastAPI | 分析中间件 |
| **部署** | Docker Compose | 容器化部署 |

## 🚀 快速开始

### Windows用户

1. **下载安装程序**
   ```
   archive-analysis-system-v1.0.exe
   ```

2. **双击安装**
   - 自动检测Docker
   - 一键部署所有服务

3. **启动系统**
   - 双击桌面快捷方式
   - 点击"启动系统"按钮
   - 等待3-5分钟

4. **访问系统**
   ```
   地址: http://localhost:8080
   用户: admin
   密码: admin
   ```

### Linux/Mac用户

```bash
# 克隆项目
git clone https://github.com/bigbangkobe/archive-analysis-system.git
cd archive-analysis-system

# 运行安装脚本
bash install.sh
```

## 📝 使用说明

### 1. 登录系统
- 访问 http://localhost:8080
- 默认用户: admin
- 默认密码: admin

### 2. 上传档案
- 进入"档案管理"模块
- 选择"批量上传"
- 选择PDF/图片文件
- 点击"开始上传"

### 3. 自动分析
- 上传完成后自动触发OCR识别
- OCR完成后自动调用大模型分析
- 生成分析报告

### 4. 查看和导出报告
- 在"分析报告"模块查看
- 支持导出为PDF/Excel

## 🛠️ 项目结构

```
archive-analysis-system/
├── services/                   # 微服务
│   ├── ocr_service/           # OCR识别服务
│   └── analysis_service/      # 分析中间件
├── docker/                     # Docker配置
│   ├── docker-compose.yml
│   └── Dockerfile.*
├── installer/                  # 安装程序
│   ├── startup.py             # Python启动器
│   └── install.sh
├── sql/                        # 数据库脚本
│   └── init.sql
└── docs/                       # 文档
    ├── INSTALL.md
    └── USER_GUIDE.md
```

## ⚙️ 系统要求

- **CPU**: 4核以上
- **内存**: 16GB
- **磁盘**: 100GB
- **Docker Desktop**: 20.10+

## 🔒 安全特性

- ✅ 完全本地离线运行
- ✅ 数据加密存储
- ✅ 细粒度权限控制
- ✅ 完整审计日志

## 📄 许可证

MIT License

## 📞 联系方式

- 📧 Email: support@example.com
- 🐛 Issues: https://github.com/bigbangkobe/archive-analysis-system/issues
