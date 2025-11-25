import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
exec(open('single-file-agent/11-agent-create-class-style-middleware.py').read())
import time

def test_multiple_calls():
    # 初始状态
    state = {"messages": [], "model_call_count": 0, "user_id": "admin"}

    print("=== 第一次调用 ===")
    state["messages"] = [{"role": "user", "content": "Hello"}]
    result1 = agent.invoke(state)
    print(f"第一次调用后的 model_call_count: {result1.get('model_call_count', 'undefined')}")

    print("\n=== 第二次调用 ===")
    # 保持之前的状态
    result2 = agent.invoke(result1)
    print(f"第二次调用后的 model_call_count: {result2.get('model_call_count', 'undefined')}")

    print("\n=== 第三次调用 ===")
    # 保持之前的状态
    result3 = agent.invoke(result2)
    print(f"第三次调用后的 model_call_count: {result3.get('model_call_count', 'undefined')}")

if __name__ == "__main__":
    test_multiple_calls()