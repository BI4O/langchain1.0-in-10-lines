from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore

load_dotenv()

# 创建 agent 和 store
llm = ChatOpenAI(model="kimi-k2")
store = InMemoryStore()

agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    store=store  # 🎯 关键：提供 store
)

def demonstrate_store_methods():
    print("🔥 所有访问 Store 的方法")
    print("=" * 50)

    # 方法1: create_agent 后直接操作 store
    print("\n📝 方法1: create_agent 后直接操作")
    store.put(("users", "user_123"), "subscription", True)
    print("✅ 已设置 user_123 为高级用户")

    # 验证存储
    user_data = store.get(("users", "user_123"), "subscription")
    print(f"🔍 验证结果: {user_data.value if user_data else 'None'}")

    # 方法2: 直接访问 agent.store
    print("\n📝 方法2: 通过 agent.store 访问")
    agent.store.put(("users", "user_456"), "subscription", True)
    print("✅ 已设置 user_456 为高级用户")

    # 验证
    user_data2 = agent.store.get(("users", "user_456"), "subscription")
    print(f"🔍 验证结果: {user_data2.value if user_data2 else 'None'}")

    # 方法3: 在中间件中访问（runtime.store）
    print("\n📝 方法3: 在中间件中访问 (runtime.store)")
    print("中间件可以通过 runtime.store 访问同一个 store 实例")

    # 方法4: 在工具中访问（runtime.store）
    print("\n📝 方法4: 在工具中访问 (runtime.store)")
    print("工具可以通过 runtime.store 访问同一个 store 实例")

    print("\n📊 总结:")
    print("• 方法1: store.put() - 直接操作")
    print("• 方法2: agent.store.put() - 通过 agent")
    print("• 方法3: runtime.store.put() - 中间件中")
    print("• 方法4: runtime.store.put() - 工具中")
    print("\n🎯 关键：所有方法访问的是同一个 store 实例！")

if __name__ == "__main__":
    demonstrate_store_methods()