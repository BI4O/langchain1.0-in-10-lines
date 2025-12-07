from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
# load_dotenv()

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(model=llm, system_prompt="You are a helpful assistant.")

if __name__ == "__main__":
    state = agent.invoke({"messages": "Hello! Who are you?"})
    print(state["messages"][-1].content)

    """Hello! I'm Kimi, your AI assistant from Moonshot AI."""