#!/usr/bin/env python3
"""测试带工具时的中间件调用情况"""

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import Callable
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="kimi-k2")

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}今天天气晴朗，温度25°C"

# 创建一个简单的计数器中间件
class CounterMiddleware:
    def __init__(self):
        self.call_count = 0

    def __call__(self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]):
        self.call_count += 1
        print(f"🔍 Middleware call #{self.call_count}")
        print(f"   Messages count: {len(request.messages)}")
        if request.messages:
            last_msg = request.messages[-1]
            print(f"   Last message type: {type(last_msg).__name__}")
            if hasattr(last_msg, 'content'):
                print(f"   Last message: {last_msg.content[:50]}...")
        return handler(request)

# 创建计数器实例
counter = CounterMiddleware()

# 将计数器转换为中间件
counting_middleware = wrap_model_call(counter)

# 创建agent
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    tools=[get_weather],
    middleware=[counting_middleware]
)

if __name__ == "__main__":
    print("=== 测试工具调用开始 ===")

    # 重置计数器
    counter.call_count = 0

    # 进行一个需要工具调用的对话
    result = agent.invoke({"messages": "北京今天天气怎么样？"})

    print(f"\n=== 测试结果 ===")
    print(f"中间件总调用次数: {counter.call_count}")
    print("调用详情:")
    for i, msg in enumerate(result["messages"]):
        print(f"  {i+1}. {type(msg).__name__}: {msg.content[:50] if hasattr(msg, 'content') else str(msg)[:50]}...")

    print(f"\n分析:")
    if counter.call_count == 2:
        print("❌ 发现预期外的第二次调用！这可能是个性能问题。")
    elif counter.call_count == 1:
        print("✅ 只有一次模型调用，正常")
    else:
        print(f"🤔 调用次数为{counter.call_count}，需要进一步分析")