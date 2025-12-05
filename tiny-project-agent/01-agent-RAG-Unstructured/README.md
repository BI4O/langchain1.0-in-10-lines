# Agent RAG with Unstructured Documents

基于LangChain的智能文档检索系统，支持PDF、图片等多种文档格式的处理和问答。

## 快速开始

### 1. 环境准备
```bash
# 安装 uv (如果还没安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目后进入目录
cd tiny-project-agent/01-agent-RAG-Unstructured
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API配置
# 主要是 BASE_URL 和各个模型的 API_KEY
```

### 3. 安装依赖并运行
```bash
# 安装依赖
uv sync

# 运行程序
uv run python main.py
```

## 功能特性

- 📄 支持PDF、PNG等多种文档格式
- 🔍 智能文档检索和问答
- 🧠 基于向量数据库的语义搜索
- 💾 本地向量存储 (ChromaDB)

## 使用说明

1. 将文档放入 `docs/` 目录
2. 运行程序后会自动处理文档并建立索引
3. 在命令行中输入问题，系统会基于文档内容回答

## 依赖说明

- Python >= 3.11
- 使用 uv 进行包管理
- 支持本地模型和OpenAI兼容API