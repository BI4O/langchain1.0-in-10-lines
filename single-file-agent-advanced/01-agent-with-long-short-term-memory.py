from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv()
llm = ChatOpenAI(model="glm-4.6")

@tool(description="you must use this tool when user mention his/her name.")
def save_user_name(runtime: ToolRuntime, user_name: str) -> str:
    """save user name when user mention his name, Must use when users mentions their names"""
    store = runtime.store
    store.put(("basic_info",),"user",{"user_name":user_name})
    return "user_name saved"

@tool
def get_user_name(runtime: ToolRuntime) -> str:
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

"""
🧠 Short term memory test: must use same CONFIG
================================ Human Message =================================

我叫小明，今年25岁，你记住了
================================== Ai Message ==================================

好的，小明！我记住了，你今年25岁。

很高兴认识你。接下来有什么可以帮你的吗？
================================ Human Message =================================

我什么名字了
================================== Ai Message ==================================

你叫小明呀。我记得的。
================================ Human Message =================================

我几岁了
================================== Ai Message ==================================

你25岁呀，我记得的。
================================ Human Message =================================

我什么名字了
================================== Ai Message ==================================

我不知道您叫什么名字。

我是一个人工智能模型，为了保护您的隐私和安全，我无法获取或记住您的任何个人信息，所以我们的对话是匿名的。

不过，如果您愿意的话，可以随时告诉我您希望我称呼您为什么。这样，在我们接下来的交流中我就可以用这个名字来称呼您了。

🧠 Long term memory test: must use tools and save structed JSON
================================ Human Message =================================

我叫小明，今年25岁，你记住了
================================== Ai Message ==================================

好的，我记住了你的名字！
Tool Calls:
  save_user_name (call_857fddad982243b997ba936b)
 Call ID: call_857fddad982243b997ba936b
  Args:
    user_name: 小明
================================= Tool Message =================================
Name: save_user_name

user_name saved
================================== Ai Message ==================================

好的，小明！我记住你的名字了。很高兴认识你！你有什么需要我帮助的吗？
================================ Human Message =================================

我什么名字了
================================== Ai Message ==================================

我来帮您查看一下您的名字。
Tool Calls:
  get_user_name (call_dade6f0c7acf460cb923c2a5)
 Call ID: call_dade6f0c7acf460cb923c2a5
  Args:
================================= Tool Message =================================
Name: get_user_name

User name: 小明
================================== Ai Message ==================================

您的名字是小明。
================================ Human Message =================================

我几岁了
================================== Ai Message ==================================

我没有关于您年龄的信息。我只能访问您的姓名信息，但无法知道您的年龄。如果您想让我记住您的姓名，可以告诉我，我会保存下来。不过关于年龄，您需要自己提供这个信息。
"""
