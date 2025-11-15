from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(model=llm,system_prompt="You are a helpful assistant.")

if __name__ == "__main__":
    # 1. streaming by values(HumanMessage, AIMessage, ToolMessage)
    for chunk in agent.stream({"messages":"Hello! Who are you?"}, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    """
    ================================ Human Message =================================

    Hello! Who are you?
    ================================== Ai Message ==================================

    Hello! I'm Kimi, your AI assistant from Moonshot AI. 
    """
