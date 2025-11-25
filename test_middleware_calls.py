#!/usr/bin/env python3
"""测试中间件重复调用问题的脚本"""

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_openai import ChatOpenAI
from typing import Callable
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="kimi-k2")

# 创建一个简单的计数器中间件
class CounterMiddleware:
    def __init__(self):
        self.call_count = 0

    def __call__(self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]):
        self.call_count += 1
        print(f"🔍 Middleware call #{self.call_count}")
        print(f"   Messages count: {len(request.messages)}")
        print(f"   Last message: {request.messages[-1].content[:50]}...")
        return handler(request)

# 创建计数器实例
counter = CounterMiddleware()

# 将计数器转换为中间件
counting_middleware = wrap_model_call(counter)

# 创建agent
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    middleware=[counting_middleware]
)

if __name__ == "__main__":
    print("=== 测试开始 ===")

    # 重置计数器
    counter.call_count = 0

    # 进行一次简单的对话
    result = agent.invoke({"messages": "Hello! Just say hi back."})

    print(f"\n=== 测试结果 ===")
    print(f"中间件总调用次数: {counter.call_count}")
    print(f"预期调用次数: 1")

    if counter.call_count > 1:
        print("❌ 发现重复调用问题！")
    else:
        print("✅ 没有重复调用问题")