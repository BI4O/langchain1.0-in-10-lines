from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.runtime import Runtime
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.store.memory import InMemoryStore

load_dotenv()

class CustomState(AgentState):
    model_call_count: int
    user_id: str

# ❌ 错误示例：只使用 state，没有使用 store
@before_model(state_schema=CustomState)
def check_login_state_only(state: CustomState, runtime: Runtime):
    """只从 state 检查登录状态"""
    is_login = state.get("is_login", False)
    print(f"🔍 State检查登录状态: {is_login}")
    return None

# ✅ 正确示例：使用 store 存储和读取用户信息
@before_model(state_schema=CustomState)
def check_login_from_store(state: CustomState, runtime: Runtime):
    """从 store 检查真实的登录状态"""
    user_id = state.get("user_id")

    # 🔑 关键：检查是否有 store 可用
    if runtime.store is None:
        print("⚠️  没有可用的 store，跳过 store 检查")
        return None

    # 从 store 读取用户登录信息
    user_info = runtime.store.get(("users", user_id), "login_status")
    is_login = user_info.value if user_info and hasattr(user_info, 'value') else False

    print(f"🔍 Store检查用户 {user_id} 登录状态: {is_login}")

    if not is_login:
        print("🚫 用户未登录，限制访问")
        return {"jump_to": "end"}
    return None

@after_model(state_schema=CustomState)
def simulate_login(state: CustomState, runtime: Runtime):
    """模拟用户登录：将登录信息存储到 store"""
    user_id = state.get("user_id")
    last_message = state["messages"][-1].content.lower()

    # 🔑 关键：检查是否有 store 可用
    if runtime.store is None:
        print("⚠️  没有可用的 store，无法存储登录信息")
        return None

    # 如果用户说"login"，就在 store 中记录登录状态
    if "login" in last_message:
        print(f"🔐 用户 {user_id} 登录成功，存储到 store")
        runtime.store.put(("users", user_id), "login_status", {
            "is_login": True,
            "login_time": "2025-01-19 10:00:00"
        })
    return None

# 创建两个 agent 对比
llm = ChatOpenAI(model="kimi-k2")

# Agent 1: 不使用 store（只依赖 state）
agent_without_store = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    # 不设置 store
    middleware=[check_login_state_only, simulate_login]
)

# Agent 2: 使用 store（真正的用户管理）
agent_with_store = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    store=InMemoryStore(),  # 🎯 关键：提供 store
    middleware=[check_login_from_store, simulate_login]
)

def demonstrate_store_difference():
    print("🔥 Agent 1: 不使用 Store（runtime.store = None）")
    print("=" * 50)

    state1 = {
        "messages": [{"role": "user", "content": "hello"}],
        "user_id": "user_123"
    }
    result1 = agent_without_store.invoke(state1)

    print("\n🔥 Agent 2: 使用 Store（runtime.store = InMemoryStore）")
    print("=" * 50)

    state2 = {
        "messages": [{"role": "user", "content": "hello"}],
        "user_id": "user_456"
    }
    result2 = agent_with_store.invoke(state2)

    print("\n📊 总结:")
    print("• Agent 1: runtime.store = None，无法使用存储功能")
    print("• Agent 2: runtime.store = InMemoryStore，可以使用存储功能")

if __name__ == "__main__":
    demonstrate_store_difference()