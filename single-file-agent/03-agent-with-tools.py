from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_core.tools import tool # * new: import tool decorator

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

# * new
@tool
def get_weather(city: str) -> str:
    """Get weather info for a city (mock implementation)."""
    return f"The weather in {city} is sunny with a high of 25°C."

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    tools=[get_weather]  # * new: add tool to agent
)

if __name__ == "__main__":
    # use stream mode to see tool usage in action
    for chunk in agent.stream(
        {"messages":"What's the weather like in Shanghai?"},
        stream_mode="values"
    ):
        msg = chunk["messages"][-1]
        msg.pretty_print()

    """
================================ Human Message =================================

What's the weather like in Shanghai?
================================== Ai Message ==================================

I'llget the weather information for Shanghai for you.
Tool Calls:
  get_weather (call_Ui7DathrHQu1yEPoRA9wUoB6)
 Call ID: call_Ui7DathrHQu1yEPoRA9wUoB6
  Args:
    city: Shanghai
================================= Tool Message =================================
Name: get_weather

The weather in Shanghai is sunny with a high of 25°C.
================================== Ai Message ==================================

Shanghai's weather today is sunny with a maximum temperature of 25°C. It's quite pleasant weather!   
    """