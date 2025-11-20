from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

# * new: import ShortTermMemory
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI(model="kimi-k2")

agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),  # * new: add short-term memory support
)

# * new: define config
config = {"configurable":{"thread_id":"1"}}

if __name__ == "__main__":
    agent.invoke({"messages":"Hello! My name is Neo"}, config=config)
    state = agent.invoke({"messages":"Who am I?"}, config=config)
    for msg in state["messages"]:
        msg.pretty_print()

"""
================================ Human Message =================================

Hello! My name is Neo
================================== Ai Message ==================================

Hello, Neo! That’s a great name—very Matrix-inspired.  
Nice to meet you. How can I help you today?
================================ Human Message =================================

Who am I?
================================== Ai Message ==================================

In every practical sense, you are Neo—the person who just told me that name. 
"""