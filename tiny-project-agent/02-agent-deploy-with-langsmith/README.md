# Agent部署到LangSmith

使用LangGraph部署Agent到LangSmith平台。

## 快速开始

### 1. 环境准备
```bash
pip install langgraph-cli
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 3. 项目结构
```
├── agent.py          # Agent定义（必须包含agent变量）
├── langgraph.json    # 部署配置
└── .env             # 环境变量
```

### 4. 运行
```bash
langgraph dev
```

访问 http://localhost:2024 查看API文档和测试界面。

## 核心文件

**agent.py**
```python
from langchain.agents import create_agent

def send_email(to: str, subject: str, body: str):
    return f"Email sent to {to}"

agent = create_agent(
    "openai:kimi-k2",
    tools=[send_email],
    system_prompt="You are an email assistant.",
)
```

**langgraph.json**
```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./agent.py:agent"
  },
  "env": ".env"
}
```