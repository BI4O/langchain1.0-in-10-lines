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
    current_state = request.state  # note：Must Init CustomState in run-code, or get "state" not found error !!!
    llm = large_llm if state.get("use_kimi_model", False) else small_llm
    return handler(request.override(model=llm))

# 4. create agent
agent = create_agent(
    model=small_llm,
    middleware=[switch_model],
    state_schema=CustomState, # * new specify state
)

if __name__ == "__main__":
    state = CustomState(messages=["hello, who model are u ?"], use_kimi_model=False)
    state = agent.invoke(state)

    # switch model
    state["use_kimi_model"]=True  # hard code 
    state["messages"].append("who model are u ?") # tricky way to use memory
    state = agent.invoke(state)

    # model can read CustomState value, yet can't modify it
    state["messages"].append("who is the value of `use_kimi_model` now ?")
    state = agent.invoke(state)

    # check output
    for msg in state["messages"]:
        msg.pretty_print()

"""
================================ Human Message =================================

hello, who model are u ?
================================== Ai Message ==================================

Hello! I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. 
================================ Human Message =================================

who model are u ?
================================== Ai Message ==================================

I’m Kimi, a large language model trained by Moonshot AI.
================================ Human Message =================================

who is the value of `use_kimi_model` now ?
================================== Ai Message ==================================

The value of `use_kimi_model` is `True` — so you’re talking to Kimi (Moonshot AI’s model), not Qwen.
"""
