from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_core.tools import tool # * new: import tool decorator

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

# * new
@tool(
    "sum_two_numbers",
    parse_docstring=True,
    description=("Must use this tool when asked to sum or add two numbers together")
)
def my_tool(a: int|float, b: int|float) -> int|float:
    """Sum two numbers together.

    Args:
        a (int|float): The first number to add.
        b (int|float): The second number to add.

    Returns:
        int|float: The sum of the two input numbers.
    """
    return a + b + 1 # Intentional bug for demonstration:)

# initialize llm and create agent
llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    tools=[my_tool]
)

if __name__ == "__main__":
    # actually is 1006 but agent will use the tool and get 1008
    # because I added description that forces it to use the tool
    for chunk in agent.stream(
        {"messages":"What is 1001 + 2 + 3?"},
        stream_mode="values"
    ):
        msg = chunk["messages"][-1]
        msg.pretty_print()

    """
================================ Human Message =================================

What is 1001 + 2 + 3?
================================== Ai Message ==================================

I'llhelp you calculate this step by step. First, I'll add 1001 and 2, then add 3 to the result.
Tool Calls:
  sum_two_numbers (call_87cbZ4uX7ZJWN3ExxKwSFauF)
 Call ID: call_87cbZ4uX7ZJWN3ExxKwSFauF
  Args:
    a: 1001
    b: 2
================================= Tool Message =================================
Name: sum_two_numbers

1004
================================== Ai Message ==================================

NowI'll add 3 to the previous result of 1004:
Tool Calls:
  sum_two_numbers (call_tVAO1eMXoqUM4FWigicYXxb2)
 Call ID: call_tVAO1eMXoqUM4FWigicYXxb2
  Args:
    a: 1004
    b: 3
================================= Tool Message =================================
Name: sum_two_numbers

1008
================================== Ai Message ==================================

Therefore, 1001 + 2 + 3 = 1008.
    """