from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool,InjectedToolCallId
from dotenv import load_dotenv
from langgraph.types import Command
from typing import Annotated
from langchain.messages import ToolMessage

# 1. load llms
load_dotenv()
llm = ChatOpenAI(model="kimi-k2")
llms1 = ChatOpenAI(model="tstars2.0")

# init subagent first
subagent1 = create_agent(model=llms1)

# 2. define tool
@tool("math_expert", description="a smart subagent to do math")
def math_subagent(query:str) -> str:
    state = subagent1.invoke({"messages":query})
    return state["messages"][-1].content

@tool("nlp_expert", description="a nlp expert good at extract entities")
def nlp_subagent(query:str, tool_call_id:Annotated[str, InjectedToolCallId]) -> Command:
    state = subagent1.invoke({"messages":query})
    return Command(update={
        # add any custom State keys here if needed
        "messages": [
            ToolMessage(
                content=state["messages"][-1].content, 
                tool_call_id=tool_call_id
            )
        ]
    })

# 3. create main-agent
agent = create_agent(
    model=llm,
    tools=[math_subagent,nlp_subagent],
    system_prompt="you are a helpful assitant"
)

if __name__ == "__main__":
    for state in agent.stream(
        {"messages":"What's 1+99+23?"},
        stream_mode="values"
    ):
        latest_msg = state["messages"][-1]
        latest_msg.pretty_print()

"""

What's 1+99+23?
================================== Ai Message ==================================

I'll use the math expert to calculate this for you.
Tool Calls:
  math_expert (math_expert:0)
 Call ID: math_expert:0
  Args:
    query: 1+99+23
================================= Tool Message =================================
Name: math_expert

The sum of 1, 99, and 23 is calculated as follows:

1. **Add 1 and 99**:  
   \(1 + 99 = 100\)

2. **Add the result to 23**:  
   \(100 + 23 = 123\)

**Final Answer:**  
\boxed{123}
================================== Ai Message ==================================

The answer is **123**.
"""

    # for state in agent.stream(
    #     {"messages":"use nlp expert to extract name and phone from 'neo: 123545'"},
    #     stream_mode="values"
    # ):
    #     latest_msg = state["messages"][-1]
    #     latest_msg.pretty_print()
"""
================================ Human Message =================================

use nlp expert to extract name and phone from 'neo: 123545'
================================== Ai Message ==================================
Tool Calls:
  nlp_expert (nlp_expert:0)
 Call ID: nlp_expert:0
  Args:
    query: extract name and phone from 'neo: 123545'
================================= Tool Message =================================
Name: nlp_expert

Name: neo Phone: 123545
================================== Ai Message ==================================

Name: neo  
Phone: 123545
"""
