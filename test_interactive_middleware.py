import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入并执行文件内容
exec(open('single-file-agent/11-agent-create-class-style-middleware.py').read())
import sys

def interactive_chat():
    """交互式对话，每次用户输入都会触发中间件打印"""
    print("=== 开始交互式对话 ===")
    print("输入 'quit' 退出对话\n")

    # 初始状态
    state = {"messages": [], "model_call_count": 0, "user_id": "admin"}

    while True:
        # 获取用户输入
        user_input = input("用户: ").strip()

        if user_input.lower() in ['quit', 'exit', '退出']:
            print("=== 对话结束 ===")
            break

        if not user_input:
            continue

        # 添加用户消息到状态
        state["messages"].append({"role": "user", "content": user_input})

        print(f"\n--- 调用 Agent (当前计数: {state.get('model_call_count', 0)}) ---")

        # 调用 agent，这会触发中间件的 before_model 和 after_model
        result = agent.invoke(state)

        # 更新状态为返回的结果
        state = result

        # 获取并打印 AI 的回复
        if result["messages"]:
            ai_message = result["messages"][-1]  # 最后一条消息通常是 AI 的回复
            if hasattr(ai_message, 'content'):
                print(f"AI: {ai_message.content}")
            else:
                print(f"AI: {ai_message}")

        print(f"--- 本次调用后总计数: {state.get('model_call_count', 0)} ---\n")

if __name__ == "__main__":
    interactive_chat()