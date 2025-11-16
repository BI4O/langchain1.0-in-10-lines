from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
# * new:
from typing_extensions import TypedDict

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

# * new: define output structure
class CustomOutput(TypedDict):
    name: str
    phone: int

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    response_format=CustomOutput  # * new: specify output structure
)

if __name__ == "__main__":
    res = agent.invoke({"messages":"Hello! I am Neo not Len, and call me on one O one, seven eight night"})
    print(res["messages"][-1].content)

    """Returning structured response: {'name': 'Neo', 'phone': 101789}"""