# LangSmith Deployment API 文档

## 概述

这是一个运行在 `localhost:2024` 的 LangSmith 部署服务，提供了完整的AI助手管理和对话API。该服务基于OpenAPI 3.1.0规范，支持无状态和有状态的AI对话。

## 核心概念解析

### 1. 助手 (Assistant)

**概念说明**：
- 助手是AI模型的一个配置实例，每个助手都有特定的功能、行为和配置
- 可以理解为不同"角色"的AI，比如邮件助手、代码助手、客服助手等
- 每个助手基于一个 `graph_id`（图ID），这个图定义了助手的行为逻辑

**实际应用**：
- 邮件助手：专门处理邮件相关任务
- 代码助手：帮助编写和调试代码
- 分析助手：处理数据分析和报告

**相关端点**：
- `POST /assistants` - 创建助手
- `GET /assistants/{assistant_id}` - 获取助手信息
- `POST /assistants/search` - 搜索助手

### 2. 线程 (Thread)

**概念说明**：
- 线程是一个对话会话的容器，用于维护多轮对话的状态和历史
- 类似于聊天窗口或对话记录，保存了用户与助手的所有交互
- 支持状态持久化，可以随时恢复对话历史

**实际应用**：
- 长期项目咨询：保持项目上下文的多轮对话
- 客户服务对话：记录完整的客户交互历史
- 教学场景：保持学习进度的连续对话

**相关端点**：
- `POST /threads` - 创建新线程
- `GET /threads/{thread_id}/history` - 获取对话历史
- `GET /threads/{thread_id}/state` - 获取线程状态

### 3. 状态 (State)

**概念说明**：
- 状态是对话的当前快照，包含了所有相关的上下文信息
- 包括用户消息、助手回复、中间计算结果等
- 支持检查点(Checkpoint)机制，可以回滚到任意历史状态

**实际应用**：
- 上下文保持：助手记住之前的对话内容
- 状态回滚：如果出错可以回到之前的正确状态
- 多任务协作：在复杂任务中保持各个步骤的状态

**相关端点**：
- `GET /threads/{thread_id}/state` - 获取当前状态
- `POST /threads/{thread_id}/state` - 更新状态
- `GET /threads/{thread_id}/state/{checkpoint_id}` - 获取特定检查点状态

## API 使用方式

### 方式一：无状态对话（推荐简单场景）

适合一次性问答，不需要保存对话历史：

```bash
# 1. 创建助手
ASSISTANT_RESPONSE=$(curl -s -X POST http://localhost:2024/assistants \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "agent",
    "name": "通用助手",
    "description": "一个通用的AI助手"
  }')

ASSISTANT_ID=$(echo $ASSISTANT_RESPONSE | jq -r '.assistant_id')

# 2. 流式对话（实时响应）
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d "{
    \"assistant_id\": \"$ASSISTANT_ID\",
    \"input\": {
      \"messages\": [
        {
          \"role\": \"user\",
          \"content\": \"你好，请介绍一下天气\"
        }
      ]
    }
  }"

# 3. 等待完整响应（适合批量处理）
curl -X POST http://localhost:2024/runs/wait \
  -H "Content-Type: application/json" \
  -d "{
    \"assistant_id\": \"$ASSISTANT_ID\",
    \"input\": {
      \"messages\": [
        {
          \"role\": \"user\",
          \"content\": \"帮我分析这段数据\"
        }
      ]
    }
  }"
```

### 方式二：有状态对话（推荐复杂场景）

适合需要保持对话历史的多轮交互：

```bash
# 1. 创建助手
ASSISTANT_RESPONSE=$(curl -s -X POST http://localhost:2024/assistants \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "agent",
    "name": "项目顾问",
    "description": "专门处理项目咨询的助手"
  }')

ASSISTANT_ID=$(echo $ASSISTANT_RESPONSE | jq -r '.assistant_id')

# 2. 创建线程
THREAD_RESPONSE=$(curl -s -X POST http://localhost:2024/threads \
  -H "Content-Type: application/json" \
  -d "{
    \"assistant_id\": \"$ASSISTANT_ID\",
    \"metadata\": {
      \"project\": \"电商平台开发\"
    }
  }")

THREAD_ID=$(echo $THREAD_RESPONSE | jq -r '.thread_id')

# 3. 在线程中进行多轮对话
# 第一轮对话
curl -X POST http://localhost:2024/threads/$THREAD_ID/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "我需要开发一个电商网站，有什么建议？"
        }
      ]
    }
  }'

# 第二轮对话（会记住第一轮的上下文）
curl -X POST http://localhost:2024/threads/$THREAD_ID/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "预算大概10万，你觉得够吗？"
        }
      ]
    }
  }'

# 4. 查看对话历史
curl -s http://localhost:2024/threads/$THREAD_ID/history | jq '.'
```

## 实际应用示例

### 示例1：邮件助手

```bash
# 创建邮件助手
MAIL_ASSISTANT=$(curl -s -X POST http://localhost:2024/assistants \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "agent",
    "name": "邮件助手",
    "description": "专门处理邮件撰写和发送的AI助手",
    "metadata": {
      "type": "email_assistant"
    }
  }')

# 使用邮件助手
MAIL_ASSISTANT_ID=$(echo $MAIL_ASSISTANT | jq -r '.assistant_id')

curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d "{
    \"assistant_id\": \"$MAIL_ASSISTANT_ID\",
    \"input\": {
      \"messages\": [
        {
          \"role\": \"user\",
          \"content\": \"帮我写一封给客户的感谢信，客户叫张三，项目名称是网站重构项目\"
        }
      ]
    }
  }"
```

### 示例2：代码助手

```bash
# 创建代码助手
CODE_ASSISTANT=$(curl -s -X POST http://localhost:2024/assistants \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "agent",
    "name": "Python代码助手",
    "description": "专门处理Python编程问题的AI助手"
  }')

CODE_ASSISTANT_ID=$(echo $CODE_ASSISTANT | jq -r '.assistant_id')

# 使用代码助手
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d "{
    \"assistant_id\": \"$CODE_ASSISTANT_ID\",
    \"input\": {
      \"messages\": [
        {
          \"role\": \"user\",
          \"content\": \"帮我写一个Python函数来计算斐波那契数列\"
        }
      ]
    }
  }"
```

## 高级功能

### 1. 助手管理

```bash
# 列出所有助手
curl -X POST http://localhost:2024/assistants/search \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "agent"}'

# 更新助手配置
curl -X PATCH http://localhost:2024/assistants/$ASSISTANT_ID \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的助手名称",
    "description": "更新后的描述"
  }'

# 删除助手
curl -X DELETE http://localhost:2024/assistants/$ASSISTANT_ID
```

### 2. 线程管理

```bash
# 搜索线程
curl -X POST http://localhost:2024/threads/search \
  -H "Content: application/json" \
  -d '{
    "assistant_id": "'$ASSISTANT_ID'",
    "limit": 10
  }'

# 复制线程（创建新的线程但保持历史）
curl -X POST http://localhost:2024/threads/$THREAD_ID/copy

# 删除线程
curl -X DELETE http://localhost:2024/threads/$THREAD_ID
```

### 3. 流式响应处理

流式响应使用 Server-Sent Events (SSE) 格式：

```javascript
// JavaScript 示例：处理流式响应
const eventSource = new EventSource('http://localhost:2024/runs/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    assistant_id: 'your-assistant-id',
    input: {
      messages: [{ role: 'user', content: 'Hello' }]
    }
  })
});

eventSource.onmessage = function(event) {
  if (event.event === 'values') {
    const data = JSON.parse(event.data);
    console.log('助手回复:', data.messages[data.messages.length - 1].content);
  }
};
```

## Python 客户端使用

### 基础 Python 客户端

基于我们优化的 `api_test.py`，这里提供一个简洁的 Python 客户端类：

```python
import requests
import json
from pprint import pprint
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:2024"

class LangSmithClient:
    """简洁的 LangSmith API 客户端"""

    def __init__(self, graph_id="agent"):
        self.graph_id = graph_id

    def check_connection(self):
        """检查服务连接"""
        try:
            r = requests.get(f"{BASE_URL}/ok", timeout=5)
            return r.status_code == 200 and r.json().get("ok")
        except:
            return False

    def _request(self, method, endpoint, json_data=None, stream=False):
        """统一的请求方法"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.request(method, url, json=json_data, headers=headers, stream=stream)
        if response.status_code not in [200, 201]:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
        return response if stream else response.json()

    def list_agents(self, name_filter=""):
        """列出所有助手（表格显示）"""
        data = {
            "metadata": {},
            "graph_id": self.graph_id,
            "name": name_filter,
            "sort_by": "created_at",
            "select": ["created_at", "assistant_id", "name", "description", "metadata", "context"]
        }
        agents = self._request("POST", "/assistants/search", data)
        if agents:
            self._print_agents_table(agents)
        return agents

    def create_thread(self):
        """创建对话线程"""
        result = self._request("POST", "/threads", {})
        return result.get('thread_id') if result else None

    def chat(self, assistant_id, message, thread_id=None, stream=True):
        """聊天对话 - 支持流式和同步"""
        if not thread_id:
            thread_id = self.create_thread()
            if not thread_id:
                return None, None

        payload = {
            "assistant_id": assistant_id,
            "input": {"messages": [{"role": "user", "content": message}]}
        }

        if stream:
            payload["config"] = {"stream_subgraphs": True}
            return self._chat_stream(thread_id, payload)
        else:
            return self._chat_sync(thread_id, payload)

    def _chat_stream(self, thread_id, payload):
        """流式聊天 - 实时显示回复"""
        print(f"\n🤖 Assistant Response:")
        print("-" * 50)

        response = self._request("POST", f"/threads/{thread_id}/runs/stream", payload, stream=True)
        if not response:
            return thread_id, None

        full_response = ""
        try:
            current_event = None
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('event: '):
                        current_event = line_str[7:]
                    elif line_str.startswith('data: ') and current_event == 'values':
                        data_str = line_str[6:]
                        if data_str.strip() and data_str.strip() != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                if 'messages' in data:
                                    for msg in data['messages']:
                                        if msg.get('type') == 'ai':
                                            content = msg.get('content', '')
                                            if content and content not in full_response:
                                                print(content, end='', flush=True)
                                                full_response += content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"\n❌ Stream error: {e}")

        print(f"\n{'-' * 50}")
        return thread_id, full_response

    def create_assistant(self, name, model="openai:kimi-k2", system_prompt="You are a helpful assistant"):
        """创建新助手"""
        payload = {
            "graph_id": self.graph_id,
            "config": {
                "configurable": {
                    "model": model,
                    "system_prompt": system_prompt,
                    "tools": []
                }
            },
            "name": name,
            "description": f"Assistant: {name}"
        }
        result = self._request("POST", "/assistants", payload)
        return result.get('assistant_id') if result else None
```

### 快速开始示例

```python
# 基础使用示例
def quick_start():
    client = LangSmithClient()

    # 1. 检查服务状态
    if not client.check_connection():
        print("❌ 服务未启动，请运行 `langgraph dev`")
        return

    # 2. 查看可用助手
    agents = client.list_agents()
    if not agents:
        print("📭 创建一个测试助手...")
        assistant_id = client.create_assistant("测试助手", system_prompt="你是一个友好的AI助手")
        agents = client.list_agents()

    # 3. 选择助手开始对话
    assistant_id = agents[0]['assistant_id']

    # 4. 流式对话（推荐）
    thread_id, response = client.chat(assistant_id, "你好！请介绍一下你自己")

    # 5. 继续在同一会话中对话
    if thread_id:
        client.chat(assistant_id, "你能帮我写一封邮件吗？", thread_id=thread_id)

if __name__ == "__main__":
    quick_start()
```

### 高级用法

```python
class ConversationManager:
    """对话管理器 - 处理复杂的多轮对话场景"""

    def __init__(self, client):
        self.client = client
        self.conversations = {}  # {conversation_name: thread_id}

    def start_conversation(self, name, assistant_id, initial_message):
        """开始新的对话会话"""
        thread_id, response = self.client.chat(assistant_id, initial_message)
        if thread_id:
            self.conversations[name] = thread_id
            print(f"✅ 开始对话 '{name}'，线程ID: {thread_id[:12]}...")
        return thread_id, response

    def continue_conversation(self, name, assistant_id, message):
        """继续已有对话"""
        thread_id = self.conversations.get(name)
        if not thread_id:
            print(f"❌ 找不到对话 '{name}'")
            return None, None

        return self.client.chat(assistant_id, message, thread_id)

    def list_conversations(self):
        """列出所有对话"""
        print(f"\n📝 活跃对话 ({len(self.conversations)} 个):")
        for name, thread_id in self.conversations.items():
            print(f"  • {name}: {thread_id[:12]}...")

# 使用示例
def advanced_example():
    client = LangSmithClient()
    manager = ConversationManager(client)

    # 创建专门的助手
    email_assistant = client.create_assistant(
        name="邮件专家",
        system_prompt="你是一个专业的邮件撰写助手"
    )

    # 开始多个对话会话
    manager.start_conversation("客户邮件", email_assistant, "帮我写一封感谢客户的邮件")
    manager.start_conversation("团队邮件", email_assistant, "帮我写一封项目进度汇报邮件")

    # 查看所有对话
    manager.list_conversations()

    # 继续特定对话
    manager.continue_conversation("客户邮件", email_assistant, "在邮件中加上具体的项目时间线")
```

### 错误处理

常见HTTP状态码：

- `200`: 成功
- `404`: 资源不存在（助手ID、线程ID等无效）
- `409`: 冲突（如重复创建）
- `422`: 请求参数验证失败

```bash
# 错误处理示例
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "invalid-id",
    "input": {"messages": []}
  }'
```

Python 客户端中的错误处理：

```python
def safe_chat_example():
    client = LangSmithClient()

    def safe_chat(assistant_id, message, max_retries=3):
        for attempt in range(max_retries):
            try:
                thread_id, response = client.chat(assistant_id, message)
                if response is not None:
                    return thread_id, response
                print(f"⚠️ 第 {attempt + 1} 次尝试失败")
            except Exception as e:
                print(f"❌ 异常: {e}")

        print("❌ 所有尝试都失败了")
        return None, None

    # 使用安全聊天
    safe_chat("your-assistant-id", "测试消息")
```

## 最佳实践

1. **选择合适的对话模式**：
   - 简单问答 → 使用无状态运行 (`/runs/*`)
   - 多轮对话 → 使用线程 (`/threads/*`)

2. **助手配置**：
   - 为不同用途创建专门的助手
   - 使用 `metadata` 字段标记助手类型和用途

3. **状态管理**：
   - 重要对话使用线程保存历史
   - 定期备份重要的线程状态

4. **性能优化**：
   - 使用流式响应提升用户体验
   - 合理设置线程和助手的数量限制

## 服务端点总览

| 端点 | 方法 | 用途 |
|------|------|------|
| `/assistants` | POST | 创建助手 |
| `/assistants/search` | POST | 搜索助手 |
| `/assistants/{id}` | GET | 获取助手 |
| `/assistants/{id}` | PATCH | 更新助手 |
| `/assistants/{id}` | DELETE | 删除助手 |
| `/threads` | POST | 创建线程 |
| `/threads/{id}` | GET | 获取线程 |
| `/threads/{id}/history` | GET | 获取历史 |
| `/threads/{id}/runs/stream` | POST | 线程内流式对话 |
| `/runs/stream` | POST | 无状态流式对话 |
| `/runs/wait` | POST | 无状态等待响应 |
| `/ok` | GET | 健康检查 |

---

*最后更新：2025-12-07*