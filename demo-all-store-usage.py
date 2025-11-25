from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.store.memory import InMemoryStore
from langgraph.runtime import Runtime

load_dotenv()

@dataclass
class Context:
    user_id: str

class CustomState(AgentState):
    user_id: str

# 方法1: 通过中间件访问 store
@before_model(state_schema=CustomState)
def check_premium_in_middleware(state: CustomState, runtime: Runtime[Context]):
    """在中间件中检查用户是否为高级用户"""
    user_id = state.get("user_id")

    # 从 store 读取用户订阅信息
    user_data = runtime.store.get(("users", user_id), "subscription")
    is_premium = user_data.value if user_data and hasattr(user_data, 'value') else False

    print(f"🔍 中间件检查用户 {user_id} 是否为高级用户: {is_premium}")

    if is_premium:
        return {"is_premium": True}  # 更新 state
    return None

# 方法2: 通过工具访问 store
@tool
def upgrade_to_premium(runtime: ToolRuntime[Context]) -> str:
    """工具：升级用户为高级用户"""
    user_id = runtime.context.user_id

    # 直接操作 store
    runtime.store.put(("users", user_id), "subscription", True)
    print(f"🔧 工具将用户 {user_id} 升级为高级用户")

    return f"用户 {user_id} 已升级为高级用户！"

@tool
def check_my_status(runtime: ToolRuntime[Context]) -> str:
    """工具：检查用户状态"""
    user_id = runtime.context.user_id

    # 从 store 读取
    subscription = runtime.store.get(("users", user_id), "subscription")
    is_premium = subscription.value if subscription else False

    return f"用户 {user_id} 状态: {'高级用户' if is_premium else '普通用户'}"

# 方法3: 在 create_agent 后直接操作 store
def manually_set_premium(agent, user_id: str, is_premium: bool = True):
    """在 agent 创建后手动设置用户状态"""
    # 获取 agent 的 store
    store = agent.store  # 🎯 关键：直接访问 agent.store

    # 手动操作 store
    store.put(("users", user_id), "subscription", is_premium)
    print(f"🔧 手动设置用户 {user_id} 为高级用户: {is_premium}")

# 创建 agent
llm = ChatOpenAI(model="kimi-k2")
store = InMemoryStore()

agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    store=store,  # 提供 store
    tools=[upgrade_to_premium, check_my_status],
    middleware=[check_premium_in_middleware],
    context_schema=Context
)

def demonstrate_all_methods():
    print("🔥 演示所有访问 store 的方法")
    print("=" * 50)

    user_id = "user_123"
    config = {"configurable": {"thread_id": "demo"}, "context": Context(user_id=user_id)}

    # 方法3: 在 agent 创建后直接操作 store
    print("\n📝 方法3: create_agent 后手动设置")
    manually_set_premium(agent, user_id, True)

    # 方法2: 通过工具验证
    print("\n📝 方法2: 通过工具检查状态")
    result1 = agent.invoke({
        "messages": [{"role": "user", "content": "检查我的状态"}],
        "user_id": user_id
    }, config=config)

    print("\n📝 方法2: 通过工具降级")
    result2 = agent.invoke({
        "messages": [{"role": "user", "content": "我要降级为普通用户"}],
        "user_id": user_id
    }, config=config)

    # 方法1: 通过中间件验证
    print("\n📝 方法1: 通过中间件检查")
    result3 = agent.invoke({
        "messages": [{"role": "user", "content": "现在检查我的状态"}],
        "user_id": user_id
    }, config=config)

    print("\n📝 直接访问 store 验证最终状态")
    final_status = store.get(("users", user_id), "subscription")
    print(f"最终状态: {final_status.value if final_status else 'None'}")

if __name__ == "__main__":
    demonstrate_all_methods()