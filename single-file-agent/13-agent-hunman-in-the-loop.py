from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware # * new
from langgraph.checkpoint.memory import InMemorySaver # must use
from dotenv import load_dotenv

# 1. load llm
load_dotenv()
llm = ChatOpenAI(model="kimi-k2")

# 2. define tools
@tool
def get_weather(city: str) -> str:
    """Get weather info for a city (mock implementation)."""
    return f"The weather in {city} is sunny with a high of 25°C."

# 3. create agent
agent = create_agent(
    model=llm,
    tools=[get_weather],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"get_weather":{"allowed_decisions": ["approve", "reject"]}}
        )
    ], 
    checkpointer=InMemorySaver() # must use short-memory to approve and execute
)

if __name__ == "__main__":
    from langgraph.types import Command

    config = {"configurable": {"thread_id": "123"}}
    state = agent.invoke({"messages":"check weather in GZ"}, config)

    # should interrupt and need invoke Command to continue
    if '__interrupt__' in state and state['__interrupt__']:
        continue_state = agent.invoke(
            # replace "approve" with "reject" will see difference
            Command(resume={"decisions": [{"type": "approve"}]}), 
            config
        )

        print("\n=== After Command Execute ===")
        for msg in continue_state["messages"]:
            msg.pretty_print()
    else:
        for msg in state["messages"]:
            msg.pretty_print()

"""
=== After Command Execute ===
================================ Human Message =================================

check weather in GZ
================================== Ai Message ==================================

I'll check the weather in Guangzhou (GZ) for you.
Tool Calls:
  get_weather (get_weather:0)
 Call ID: get_weather:0
  Args:
    city: Guangzhou
================================= Tool Message =================================
Name: get_weather

The weather in Guangzhou is sunny with a high of 25°C.
================================== Ai Message ==================================

The weather in Guangzhou (GZ) is sunny with a high of 25°C today.
"""
 