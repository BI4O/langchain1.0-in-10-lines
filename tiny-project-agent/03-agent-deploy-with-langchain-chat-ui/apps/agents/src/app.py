from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain.tools import tool

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    return f"The current weather in {location} is sunny with a temperature of 25°C."

agent = create_agent(model=llm, system_prompt="You are a helpful assistant.", tools=[get_weather])

if __name__ == "__main__":
    # state = agent.invoke({"messages": "Hello! Who are you?"})
    # print(state["messages"][-1].content)
    for i in agent.stream({"messages": "今天广州天气如何"}, stream_mode="values"):
        i["messages"][-1].pretty_print()

    """Hello! I'm Kimi, your AI assistant from Moonshot AI."""