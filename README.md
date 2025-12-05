# LangChain 1.0 in 10 Lines

极简代码学习LangChain 1.0核心功能，每个文件演示一个具体概念。

## 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install langchain langchain-openai langgraph python-dotenv

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API配置
```

### 2. 运行示例

#### 基础学习 (single-file-agent)
```bash
# 按数字顺序学习
python single-file-agent/00-agent-with-nothing.py          # 最简单的Agent
python single-file-agent/01-agent-streaming.py            # 流式输出
python single-file-agent/02-agent-structure-output.py     # 结构化输出
python single-file-agent/03-agent-with-tools.py           # 工具使用
python single-file-agent/06-agent-with-short-memory.py    # 记忆管理
```

#### 高级功能 (single-file-agent-advanced)
```bash
python single-file-agent-advanced/01-agent-with-long-short-term-memory.py
```

#### 完整项目 (tiny-project-agent)
```bash
cd tiny-project-agent/01-agent-RAG-Unstructured
cp .env.example .env
# 编辑 .env 配置API
uv sync
uv run python main.py
```

## 项目结构

- `single-file-agent/` - 基础学习示例 (按00-12顺序学习)
- `single-file-agent-advanced/` - 高级功能示例
- `tiny-project-agent/` - 完整的RAG项目

## 学习路径

1. **初学者**: 按 `00→12` 顺序学习基础示例
2. **进阶**: 探索 `advanced` 目录的高级功能
3. **实战**: 运行 `tiny-project-agent` 中的RAG项目

每个文件专注一个功能点，代码极简，开箱即用。
