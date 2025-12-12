# Agent Chat App

一个基于 LangGraph 的聊天应用，支持使用 Python LangChain 作为后端。

## 🚀 从 JavaScript 切换到 Python LangChain

本项目原本使用 JavaScript LangGraph，但可以轻松切换到 Python LangChain。以下是完整的迁移步骤：

### 第一步：创建项目
```bash
npx create-agent-chat-app
```
**重要提示：** 创建过程中，当询问是否安装依赖时，选择 **"否"（No）**，因为我们后面会清理并使用 Python 代码。

### 第二步：清理 agents 目录
删除 `apps/agents/` 目录下的所有内容：
```bash
rm -rf apps/agents/src apps/agents/node_modules apps/agents/package.json apps/agents/tsconfig.json apps/agents/eslint.config.js
```

### 第三步：编写 Python LangChain 代码
在 `apps/agents/src/` 目录中创建你的 Python agent：

示例 `apps/agents/src/app.py`：
```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 LLM 和创建 agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(model=llm, system_prompt="You are a helpful assistant.")

if __name__ == "__main__":
    state = agent.invoke({"messages": "Hello! Who are you?"})
    print(state["messages"][-1].content)
```

创建 `apps/agents/requirements.txt`：
```
langchain
langchain-openai
python-dotenv
```

### 第四步：配置 langgraph.json
修改或创建 `./langgraph.json` 文件：

**重要：** 不要包含 `node_version` 字段，因为使用的是 Python！

```json
{
  "dependencies": [
    "."
  ],
  "graphs": {
    "agent": "./apps/agents/src/app.py:agent"
  },
  "env": ".env"
}
```

### 第五步：修改启动命令
修改根目录 `package.json` 中的 `scripts.dev`：

```json
{
  "scripts": {
    "dev": "concurrently \"turbo dev --filter=web\" \"langgraph dev --no-browser\""
  }
}
```

### 运行项目
在运行之前，先安装前端依赖和 Python 依赖：

```bash
# 安装前端依赖
pnpm install

# 安装 Python 依赖
cd apps/agents && pip install -r requirements.txt && cd ../..

# 启动项目
pnpm dev
```

这将同时启动：
- 前端：http://localhost:3000 (Next.js React 应用)
- 后端：http://localhost:2024 (Python LangGraph API)

## 📁 项目结构

```
├── apps/
│   ├── web/          # React/Next.js 前端
│   └── agents/       # Python LangChain 后端
│       ├── src/
│       │   └── app.py     # Python agent 代码
│       └── requirements.txt
├── langgraph.json    # LangGraph 配置（指向 Python）
└── package.json      # 项目配置
```

## 🔧 环境变量

在 `.env` 文件中配置：
```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url  # 可选，如使用 Kimi 等
```

## 📝 注意事项

1. **Python LangGraph CLI**：确保系统中已安装 Python 版本的 LangGraph CLI
2. **端口配置**：前端默认 3000 端口，后端默认 2024 端口
3. **agent 对象**：Python 文件中必须导出名为 `agent` 的对象
4. **路径格式**：`langgraph.json` 中使用 `/` 而不是 `:` 作为分隔符