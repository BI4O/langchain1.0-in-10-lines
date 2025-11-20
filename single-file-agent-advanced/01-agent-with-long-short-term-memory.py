from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv()

llm = ChatOpenAI(model="kimi-k2-0905")

class Context:
    user_name: str

@tool(description="you must use this tool when user mention his/her name.")
def save_user_name(runtime: ToolRuntime[Context], user_name: str) -> str:
    """save user name when user mention his name, Must use when users mentions their names"""
    store = runtime.store
    store.put(("basic_info",),"user",{"user_name":user_name})
    return "user_name saved"

@tool
def get_user_name(runtime: ToolRuntime[Context]) -> str:
    """fetch user name"""
    store = runtime.store
    try:
        info = store.get(("basic_info",),"user")
        return f"User name: {info.value['user_name']}"
    except:
        return "No user name found"

short_mem_agent = create_agent(
    model=llm,
    system_prompt="""You are a helpful assistant.""",
    checkpointer=InMemorySaver()
)

long_mem_agent = create_agent(
    model=llm,
    system_prompt="""You are a helpful assistant.""",
    tools=[save_user_name, get_user_name],
    store=InMemoryStore()
)

if __name__ == "__main__":
    # === 短期记忆演示 ===
    print("🧠 Short term memory test: must use same CONFIG")
    chat1_config = {"configurable": {"thread_id": "chat_1"}}
    chat2_config = {"configurable": {"thread_id": "chat_2"}}

    # short-term-memory should work in same chat(chat1_config)
    for state in short_mem_agent.stream({"messages":"我叫小明，今年25岁，你记住了"},chat1_config,stream_mode="values"):
        state["messages"][-1].pretty_print()
    for state in short_mem_agent.stream({"messages":"我什么名字了"},chat1_config,stream_mode="values"):
        state["messages"][-1].pretty_print()
    for state in short_mem_agent.stream({"messages":"我几岁了"},chat1_config,stream_mode="values"):
        state["messages"][-1].pretty_print()
    # should falid in chat2(chat2_config)
    for state in short_mem_agent.stream({"messages":"我什么名字了"},chat2_config,stream_mode="values"):
        state["messages"][-1].pretty_print()


    print("🧠 Long term memory test: must use tools and save structed JSON")
    # Long-term-memory should work with tools
    for state in long_mem_agent.stream({"messages":"我叫小明，今年25岁，你记住了"},stream_mode="values"):
        state["messages"][-1].pretty_print()
    for state in long_mem_agent.stream({"messages":"我什么名字了"},stream_mode="values"):
        state["messages"][-1].pretty_print()
    for state in long_mem_agent.stream({"messages":"我几岁了"},stream_mode="values"):
        state["messages"][-1].pretty_print()  # should faild cuz age not saved !
