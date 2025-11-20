from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pprint import pprint
# * new: use customize middleware
from langgraph.runtime import Runtime
from langchain.agents.middleware import (
    before_model,after_model,
    AgentState,
    hook_config # new: import hook_config for jump functionality
)
from langgraph.store.memory import InMemoryStore

load_dotenv()

class CustomState(AgentState):
    model_call_count: int
    user_name: str
    is_login: bool

# runtime is like immutable info in Agent
@before_model(state_schema=CustomState, can_jump_to=["end"])
def count_model_calls(state: CustomState, runtime: Runtime):
    print("Human: ", state["messages"][-1].content)
    # simulate limitation for non-login users
    if state.get('model_call_count',0) >= 2 and state.get('is_login',False) == False:
        print(f"AI: 🛑 model call times exceed, {state.get('user_name','')} please login to release")
        return {"jump_to": "end"}
    return None

@after_model(state_schema=CustomState)
def increment_count(state: CustomState, runtime: Runtime):
    print("AI: ",state["messages"][-1].content)
    return {"model_call_count": state.get("model_call_count",0) + 1}

llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    store=InMemoryStore(),
    middleware=[count_model_calls, increment_count]  # * new: add decorator-style middleware functions
)

if __name__ == "__main__":
    # use middleware to print rather than stream mode
    state = {
        "messages": [{"role": "user", "content": "hello ~"}], 
        "model_call_count": 0, 
        "user_name": "Neooooo", 
        "is_login": False
    }
    state = agent.invoke(state)

    state["messages"].append({"role": "user", "content": "who are u ?"})
    state = agent.invoke(state)

    state["messages"].append({"role": "user", "content": "whats the weather ?"})
    state = agent.invoke(state)

    state["messages"].append({"role": "user", "content": "hello ?"})
    state = agent.invoke(state)

    state["is_login"] = True  # simulate user login operate
    state["messages"].append({"role": "user", "content": "How are u ?"})
    state = agent.invoke(state)

    print(f"\ntotal model call: {state.get('model_call_count', 0)}")
    print(f"messages count: {len(state['messages'])}")

"""
Human:  hello ~
AI:  Hello! 😊 How can I help you today?
Human:  who are u ?
AI:  I’m Kimi, a large language model trained by Moonshot AI.
Human:  whats the weather ?
AI: 🛑 model call times exceed, Neooooo please login to release
Human:  hello ?
AI: 🛑 model call times exceed, Neooooo please login to release
Human:  How are u ?
AI:  Hey! I’m doing great—thanks for asking! 😊 How about you?

total model call: 3
messages count: 8
"""