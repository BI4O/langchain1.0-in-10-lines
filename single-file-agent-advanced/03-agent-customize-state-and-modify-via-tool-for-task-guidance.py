from langchain.agents import create_agent, AgentState
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage, HumanMessage
from dotenv import load_dotenv
from typing import Optional, Literal

# 1. load llm
load_dotenv()
llm = ChatOpenAI(model="kimi-k2")

# 2. customize State
class CustomState(AgentState):
    jack_sizes: Optional[Literal["S","M","L","XL"]]
    pant_sizes: Optional[int]
    material_preference: Optional[Literal["cotton", "wool", "linen", "silk"]]
    current_step: Optional[Literal["asking_jacket", "asking_pant", "asking_material", "completed"]]

# 3. prompt design
SYSTEM = """
You are a suit customization expert. Follow this exact sequence:

1. Ask for jacket size (S, M, L, XL)
2. Ask for pant size (28, 30, 32, 34)
3. Ask for material preference (cotton, wool, linen, silk)

IMPORTANT RULES:
- Material choice applies to the ENTIRE SUIT (both jacket and pants)
- If user tries to specify different materials for different pieces, CORRECT them
- Only recommend products after collecting ALL THREE pieces of information
- Once user confirms the final combination, call save_all_info tool

Available Options:
- Jacket Sizes: S, M, L, XL
- Pant Sizes: 28, 30, 32, 34
- Materials: cotton, wool, linen, silk (ONE material for complete suit)

Example: When user says "yes that's correct", immediately call save_all_info(jacket="L", pant=30, material="cotton").
"""

# 4. define tool for confirmation
@tool
def save_all_info(jacket: str, pant: int, material: str, runtime: ToolRuntime) -> Command:
    """save all suit customization"""
    tool_call_id = runtime.tool_call_id
    return Command(update={
        "messages": [
            ToolMessage(content=f"Saved: Jacket {jacket}, Pants {pant}, Material {material}", 
            tool_call_id=tool_call_id)
            ],
        "jack_sizes": jacket,
        "pant_sizes": pant,
        "material_preference": material,
        "current_step": "completed"
    }) 


# 5. create agent
agent = create_agent(
    model=llm,
    tools=[save_all_info],
    system_prompt=SYSTEM,
    state_schema=CustomState,
)

if __name__ == "__main__":
    state = agent.invoke({"messages": [HumanMessage(content="hello, how are u?")]})

    state["messages"].append(HumanMessage(content="how about XL"))
    state = agent.invoke(state)

    state["messages"].append(HumanMessage(content="30 is enough, and i prefer silk on pants"))
    state = agent.invoke(state)

    state["messages"].append(HumanMessage(content="I think XL is not good , switch to L plz"))
    state = agent.invoke(state)

    state["messages"].append(HumanMessage(content="No i mean in terms of jacket, i like cotton"))
    state = agent.invoke(state)

    state["messages"].append(HumanMessage(content="ok cotton for all"))
    state = agent.invoke(state)

    state["messages"].append(HumanMessage(content="yes that's correct"))
    state = agent.invoke(state)

    for msg in state["messages"]:
        msg.pretty_print()

    print(f"Final state - Jacket: {state.get('jack_sizes', '')}")
    print(f"Final state - Pant: {state.get('pant_sizes', '')}")
    print(f"Final state - Material: {state.get('material_preference', '')}")
    print(f"Final state - Step: {state.get('current_step', '')}")