#!/usr/bin/env python3
"""优化后的中间件示例 - 解决重复调用性能问题"""

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from typing import Callable
from dotenv import load_dotenv
import time

load_dotenv()

llm = ChatOpenAI(model="kimi-k2")

@tool
def search_web(query: str) -> str:
    """搜索网络信息"""
    time.sleep(0.5)  # 模拟网络延迟
    return f"关于'{query}'的搜索结果：这是一个模拟的搜索结果"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)  # 注意：实际应用中不要用eval
        return f"计算结果: {result}"
    except:
        return "计算错误：无效的表达式"

# 优化后的中间件实现
@wrap_model_call
def optimized_tool_selector(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]):
    """优化后的工具选择中间件 - 避免重复执行复杂逻辑"""

    # 判断调用阶段
    messages = request.messages
    is_initial_call = len(messages) <= 2
    is_tool_result_call = (
        len(messages) >= 3 and
        hasattr(messages[-1], '__class__') and
        messages[-1].__class__.__name__ == "ToolMessage"
    )

    if is_initial_call:
        # 🚀 首次调用 - 执行完整的工具选择逻辑
        print("🎯 [首次调用] 执行工具选择逻辑")

        # 示例：根据消息内容动态选择工具
        last_message = messages[-1].content.lower() if messages else ""

        if "计算" in last_message or any(op in last_message for op in ["+", "-", "*", "/"]):
            print("   → 选择计算工具")
            request = request.override(tools=[calculate])
        elif "搜索" in last_message or "查询" in last_message:
            print("   → 选择搜索工具")
            request = request.override(tools=[search_web])
        else:
            print("   → 提供所有工具")
            request = request.override(tools=[search_web, calculate])

    elif is_tool_result_call:
        # ⚡ 工具结果处理 - 跳过复杂逻辑，直接执行
        print("⚡ [工具结果] 快速处理，跳过工具选择")
        # 不修改request，直接传递给handler

    else:
        # 🔄 其他情况 - 轻量级处理
        print("🔄 [其他调用] 轻量级处理")

    # 执行模型调用
    start_time = time.time()
    result = handler(request)
    end_time = time.time()

    print(f"   ⏱️  模型调用耗时: {end_time - start_time:.2f}s")
    return result

# 创建优化后的agent
optimized_agent = create_agent(
    model=llm,
    system_prompt="你是一个有用的助手。根据用户的问题选择合适的工具来回答。",
    tools=[search_web, calculate],  # 提供所有工具，中间件会动态选择
    middleware=[optimized_tool_selector]
)

# 对比：未优化的agent（重复执行逻辑）
@wrap_model_call
def unoptimized_middleware(request: ModelRequest, handler):
    """未优化的中间件 - 每次都执行完整逻辑"""
    print("🐌 [未优化] 执行完整工具选择逻辑")

    # 每次都执行复杂的工具选择逻辑
    messages = request.messages
    last_message = messages[-1].content.lower() if messages else ""

    if "计算" in last_message or any(op in last_message for op in ["+", "-", "*", "/"]):
        request = request.override(tools=[calculate])
        print("   → 选择计算工具")
    else:
        request = request.override(tools=[search_web, calculate])
        print("   → 选择搜索工具")

    start_time = time.time()
    result = handler(request)
    end_time = time.time()

    print(f"   ⏱️  模型调用耗时: {end_time - start_time:.2f}s")
    return result

unoptimized_agent = create_agent(
    model=llm,
    system_prompt="你是一个有用的助手。",
    tools=[search_web, calculate],
    middleware=[unoptimized_middleware]
)

if __name__ == "__main__":
    print("=== 性能对比测试 ===\n")

    test_queries = [
        "帮我搜索一下人工智能的最新发展",
        "计算 123 + 456 等于多少？"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"📝 测试 {i}: {query}")
        print("=" * 50)

        print("\n🚀 优化版 Agent:")
        start_time = time.time()
        result_opt = optimized_agent.invoke({"messages": query})
        opt_time = time.time() - start_time

        print("\n🐌 未优化版 Agent:")
        start_time = time.time()
        result_unopt = unoptimized_agent.invoke({"messages": query})
        unopt_time = time.time() - start_time

        print(f"\n📊 性能对比:")
        print(f"   优化版总耗时: {opt_time:.2f}s")
        print(f"   未优化版总耗时: {unopt_time:.2f}s")
        print(f"   性能提升: {((unopt_time - opt_time) / unopt_time * 100):.1f}%")

        print("\n" + "=" * 60 + "\n")