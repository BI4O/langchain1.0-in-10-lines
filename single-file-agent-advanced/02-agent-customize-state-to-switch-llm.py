from langchain.agents import create_agent, AgentState
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from dotenv import load_dotenv
from typing import Callable

# 1. load llm
load_dotenv()
small_llm = ChatOpenAI(model="qwen3-coder-plus")
large_llm = ChatOpenAI(model="kimi-k2")

# 2. define state
class CustomState(AgentState):
    use_kimi_model: bool

# 3. define middleware
@wrap_model_call
def switch_model(request:ModelRequest, handler:Callable[[ModelRequest], ModelResponse]):
    current_state = request.state
    llm = large_llm if state["use_kimi_model"] else small_llm
    return handler(request.override(model=llm))

# 4. define agent
agent = create_agent(
    model=small_llm,
    middleware=[switch_model],
    state_schema=CustomState
)

if __name__ == "__main__":
    state = CustomState(messages=["hello, who model are u ?"], use_kimi_model=False)
    state = agent.invoke(state)

    # switch model
    state["use_kimi_model"]=True
    state["messages"].append("who model are u ?")
    state = agent.invoke(state)

    # check output
    for msg in state["messages"]:
        msg.pretty_print()

"""
================================ Human Message =================================

hello, who model are u ?
================================== Ai Message ==================================

Hello! I'm Qwen, a large-scale language model developed by Tongyi Lab. 
================================ Human Message =================================

who model are u ?
================================== Ai Message ==================================

I'm Kimi, a large language model trained by Moonshot AI.
"""
