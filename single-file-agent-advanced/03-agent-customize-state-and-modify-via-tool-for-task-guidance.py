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

"""
================================ Human Message =================================

hello, how are u?
================================== Ai Message ==================================

Hello! I'm doing great, thank you for asking! I'm excited to help you customize your perfect suit today.

Let's start with the first step - what jacket size would you like? The available options are S, M, L, or XL.
================================ Human Message =================================

how about XL
================================== Ai Message ==================================

Perfect! XL jacket it is.

Now for step 2 - what pant size would you like? The available options are 28, 30, 32, or 34.
================================ Human Message =================================

30 is enough, and i prefer silk on pants
================================== Ai Message ==================================

Great choice on pant size 30!

I need to clarify something important about materials - the material you choose applies to the ENTIRE suit (both jacket and pants). So if you want silk, it will be silk for both the jacket AND the pants together. You can't have different materials for different pieces.

So to confirm, would you like your complete suit (jacket and pants) to be made of silk?
================================ Human Message =================================

I think XL is not good , switch to L plz
================================== Ai Message ==================================

No problem! I'll update that to size L for the jacket.

So we have:
- Jacket: L
- Pants: 30
- Material: silk for the complete suit (both jacket and pants)

Is this combination correct?
================================ Human Message =================================

No i mean in terms of jacket, i like cotton
================================== Ai Message ==================================

I understand you want to change the material choice! So let me clarify:

You want:
- Jacket: L
- Pants: 30  
- Material: cotton for the complete suit (both jacket and pants together)

Is this correct?
================================ Human Message =================================

ok cotton for all
================================== Ai Message ==================================

Perfect! Let me confirm your complete suit customization:

- Jacket: L
- Pants: 30
- Material: cotton (for the entire suit)

Is this correct?
================================ Human Message =================================

yes that's correct
================================== Ai Message ==================================
Tool Calls:
  save_all_info (save_all_info:0)
 Call ID: save_all_info:0
  Args:
    jacket: L
    pant: 30
    material: cotton
================================= Tool Message =================================
Name: save_all_info

Saved: Jacket L, Pants 30, Material cotton
================================== Ai Message ==================================

Excellent! Your suit customization has been saved:
- Jacket: L
- Pants: 30
- Material: cotton

Thank you for choosing our suit customization service! Is there anything else I can help you with today?
Final state - Jacket: L
Final state - Pant: 30
Final state - Material: cotton
Final state - Step: completed
"""