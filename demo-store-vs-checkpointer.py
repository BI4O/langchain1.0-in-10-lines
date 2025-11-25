from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

class CustomState(AgentState):
    model_call_count: int
    user_id: str

# Store 版本：跨线程持久化
@before_model(state_schema=CustomState, can_jump_to=["end"])
def count_with_store(state: CustomState, runtime):
    count = state.get("model_call_count", 0)
    print(f"=== Store版本 - Before Model Call ===")
    print(f"model call count: {count}")
    print(f"user_id: {state.get('user_id', 'unknown')}")

    if count >= 2:
        print("🛑 Store版本：调用次数超过限制")
        return {"jump_to": "end"}
    return None

@after_model(state_schema=CustomState)
def increment_with_store(state: CustomState, runtime):
    old_count = state.get("model_call_count", 0)
    new_count = old_count + 1
    print(f"=== Store版本 - After Model Response ===")
    print(f"count updated from {old_count} to {new_count}")
    return {"model_call_count": new_count}

# Checkpointer 版本：线程内持久化
@before_model(state_schema=CustomState, can_jump_to=["end"])
def count_with_checkpointer(state: CustomState, runtime):
    count = state.get("model_call_count", 0)
    print(f"=== Checkpointer版本 - Before Model Call ===")
    print(f"model call count: {count}")
    print(f"user_id: {state.get('user_id', 'unknown')}")

    if count >= 2:
        print("🛑 Checkpointer版本：调用次数超过限制")
        return {"jump_to": "end"}
    return None

@after_model(state_schema=CustomState)
def increment_with_checkpointer(state: CustomState, runtime):
    old_count = state.get("model_call_count", 0)
    new_count = old_count + 1
    print(f"=== Checkpointer版本 - After Model Response ===")
    print(f"count updated from {old_count} to {new_count}")
    return {"model_call_count": new_count}

# 创建两个 agent
llm = ChatOpenAI(model="kimi-k2")

# Store 版本
agent_with_store = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    store=InMemoryStore(),  # 使用 store
    middleware=[count_with_store, increment_with_store]
)

# Checkpointer 版本
agent_with_checkpointer = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),  # 使用 checkpointer
    middleware=[count_with_checkpointer, increment_with_checkpointer]
)

def test_store_vs_checkpointer():
    print("🔥 测试 Store 版本（无线程ID，每次调用都是独立的）")
    print("=" * 50)

    state1 = {"messages": [], "model_call_count": 0, "user_id": "user1"}
    state1["messages"].append({"role": "user", "content": "你好"})
    result1 = agent_with_store.invoke(state1)

    state2 = result1
    state2["messages"].append({"role": "user", "content": "你是谁？"})
    result2 = agent_with_store.invoke(state2)

    print(f"\nStore版本最终计数: {result2.get('model_call_count', 0)}")

    print("\n🔥 测试 Checkpointer 版本（需要线程ID，支持状态恢复）")
    print("=" * 50)

    config = {"configurable": {"thread_id": "conversation_1"}}

    # 第一次调用
    state1 = {"messages": [], "model_call_count": 0, "user_id": "user1"}
    state1["messages"].append({"role": "user", "content": "你好"})
    result1 = agent_with_checkpointer.invoke(state1, config=config)

    # 第二次调用（基于线程ID自动恢复状态）
    state2 = {"messages": [], "user_id": "user1"}  # 注意：不需要传 model_call_count
    state2["messages"].append({"role": "user", "content": "你是谁？"})
    result2 = agent_with_checkpointer.invoke(state2, config=config)

    print(f"\nCheckpointer版本最终计数: {result2.get('model_call_count', 0)}")

if __name__ == "__main__":
    test_store_vs_checkpointer()