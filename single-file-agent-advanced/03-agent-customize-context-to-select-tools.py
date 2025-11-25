from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable
from dotenv import load_dotenv
# * new
from dataclasses import dataclass

# 1. load llm
load_dotenv()
llm = ChatOpenAI(model="kimi-k2")

# 2. customize context
@dataclass
class CustomContext:
    session_id: str
    is_logged_in: bool

# 3. tools
@tool
def public_get_secret_num():
    """get secret number"""
    return 3

@tool
def private_get_secret_num():
    """get secret number"""
    return 9

# 4. define middleware
@wrap_model_call
def tools_selector(request:ModelRequest, handler:Callable[[ModelRequest], ModelResponse]):
    context = request.runtime.context
    # use .attr of context not .get() nor dict[key]
    available_tools = [private_get_secret_num] if context.is_logged_in \
        else [public_get_secret_num]
    return handler(request.override(tools=available_tools))

# 5. create agent
agent = create_agent(
    model=llm,
    tools=[public_get_secret_num, private_get_secret_num],
    middleware=[tools_selector],
    context_schema=CustomContext
)

if __name__ == "__main__":
    # context = CustomContext(session_id="s1",is_logged_in=False) # should get 3
    context = CustomContext(session_id="s2",is_logged_in=True) # should get 9

    for state in agent.stream(
        {"messages":"what is the secret num?"}, 
        context=context, 
        stream_mode="values"
    ):
        state["messages"][-1].pretty_print()

"""
================================ Human Message =================================

what is the secret num?
================================== Ai Message ==================================

I'll get the secret number for you.
Tool Calls:
  private_get_secret_num (private_get_secret_num:0)
 Call ID: private_get_secret_num:0
  Args:
================================= Tool Message =================================
Name: private_get_secret_num

9
================================== Ai Message ==================================

The secret number is 9.
"""