from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents.middleware import after_model, AgentState
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

class CustomState(AgentState):
    model_call_count: int
    user_id: str

@after_model(state_schema=CustomState)
def show_state(state: CustomState, runtime):
    print(f"当前状态: messages={len(state['messages'])}, count={state.get('model_call_count', 0)}")
    return None

llm = ChatOpenAI(model="kimi-k2")

# Store 版本
agent_store = create_agent(
    model=llm,
    store=InMemoryStore(),
    middleware=[show_state]
)

# Checkpointer 版本
agent_checkpoint = create_agent(
    model=llm,
    checkpointer=InMemorySaver(),
    middleware=[show_state]
)

def demonstrate_difference():
    print("🔥 Store 版本演示")
    print("特点：手动管理状态，每次都要传完整状态")

    # 第一次调用
    state1 = {"messages": [{"role": "user", "content": "Hi"}], "model_call_count": 5}
    print(f"传入状态: {state1}")
    result1 = agent_store.invoke(state1)

    # 第二次调用 - 必须手动传递更新后的状态
    state2 = {"messages": [{"role": "user", "content": "How are you?"}], "model_call_count": 1}
    print(f"传入状态: {state2}")
    result2 = agent_store.invoke(state2)

    print("\n🔥 Checkpointer 版本演示")
    print("特点：自动管理状态，基于thread_id恢复")

    config = {"configurable": {"thread_id": "demo_thread"}}

    # 第一次调用
    state1 = {"messages": [{"role": "user", "content": "Hi"}], "model_call_count": 5}
    print(f"传入状态: {state1}")
    result1 = agent_checkpoint.invoke(state1, config=config)

    # 第二次调用 - 可以省略状态，checkpointer会自动恢复
    state2 = {"messages": [{"role": "user", "content": "How are you?"}]}  # 注意：没传count
    print(f"传入状态: {state2}")
    result2 = agent_checkpoint.invoke(state2, config=config)

    # 查看线程状态历史
    print("\n📋 Checkpointer 状态历史:")
    history = agent_checkpoint.get_state_history(config)
    for i, snapshot in enumerate(list(history)[:3]):  # 只显示前3个
        print(f"  快照{i+1}: {snapshot.values}")

if __name__ == "__main__":
    demonstrate_difference()