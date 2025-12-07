import requests
import json
from pprint import pprint
from tabulate import tabulate

BASE_URL = "http://127.0.0.1:2024"

class LangSmithClient:
    """简洁的 LangSmith API 客户端"""

    def __init__(self, graph_id="agent"):
        self.graph_id = graph_id
        self.check_connection()

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
        """列出所有助手"""
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

    def _print_agents_table(self, agents):
        """打印助手表格"""
        if not agents:
            print("📭 No agents found.")
            return

        table = [
            [
                i + 1,
                agent['assistant_id'][:12] + '...',
                agent['name'],
                agent.get('description', 'N/A'),
                agent['metadata'].get('created_by', 'N/A'),
                agent['created_at'][:19].replace('T', ' ')
            ]
            for i, agent in enumerate(agents)
        ]

        headers = ['#', 'Assistant ID', 'Name', 'Description', 'Created By', 'Created At']
        print("\n" + tabulate(table, headers=headers, tablefmt='grid') + "\n")

    def create_thread(self):
        """创建对话线程"""
        result = self._request("POST", "/threads", {})
        return result.get('thread_id') if result else None

    def chat(self, assistant_id, message, thread_id=None, stream=True):
        """聊天对话"""
        # 创建线程（如果需要）
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
        """流式聊天"""
        # 提取用户消息并显示
        user_message = payload["input"]["messages"][0]["content"]
        print(f"\n👤 User: {user_message}")
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
                        current_event = line_str[7:]  # 获取事件类型
                    elif line_str.startswith('data: ') and current_event == 'values':
                        data_str = line_str[6:]  # 获取数据
                        if data_str.strip() and data_str.strip() != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                if 'messages' in data:
                                    for msg in data['messages']:
                                        # 查找 AI 类型的消息
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

    def _chat_sync(self, thread_id, payload):
        """同步聊天"""
        # 提取用户消息并显示
        user_message = payload["input"]["messages"][0]["content"]
        print(f"\n👤 User: {user_message}")
        print(f"\n🤖 Assistant Response (Sync):")
        print("-" * 50)

        result = self._request("POST", f"/threads/{thread_id}/runs", payload)
        if result:
            pprint(result)
        print("-" * 50)
        return thread_id, result

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


def main():
    """主函数示例"""
    client = LangSmithClient()

    # 检查连接
    if not client.check_connection():
        print("❌ 无法连接到服务，请确保运行 `langgraph dev`")
        return

    # 列出助手
    agents = client.list_agents()
    if not agents:
        print("📭 没有找到助手，创建一个测试助手...")
        assistant_id = client.create_assistant("Test Assistant", system_prompt="你是一个友好的助手")
        if assistant_id:
            print(f"✅ 创建助手成功: {assistant_id}")
            agents = client.list_agents()
        else:
            return

    # 选择第一个助手
    assistant_id = agents[0]['assistant_id']
    print(f"🎯 选择助手: {agents[0]['name']}")

    # 开始对话
    thread_id = None
    conversations = [
        "你好！请介绍一下你自己。",
        "你能帮我写一封简单的邮件吗？给bob@qq.com,让他快点还钱",
        "总结一下我们的对话。"
    ]

    for i, message in enumerate(conversations, 1):
        print(f"\n=== 对话 {i} ===")
        thread_id, response = client.chat(assistant_id, message, thread_id, stream=True)

        if not response:
            print("❌ 对话失败")
            break

    print("\n✅ 对话完成！")


if __name__ == "__main__":
    main()