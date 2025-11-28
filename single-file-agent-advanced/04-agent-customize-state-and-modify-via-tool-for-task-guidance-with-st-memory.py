from langchain.agents import create_agent, AgentState
from langchain_openai import ChatOpenAI
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
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

# 5. create checkpointer
checkpointer = InMemorySaver()

# 6. create agent with checkpointer
agent = create_agent(
    model=llm,
    tools=[save_all_info],
    system_prompt=SYSTEM,
    state_schema=CustomState,
    checkpointer=checkpointer,  # * new: add short-term memory
)

if __name__ == "__main__":
    # ✅ use invoke + checkpointer to memorize, rather than state["messages"].append(msg)
    config = {"configurable": {"thread_id": "suit_customization_1"}}

    agent.invoke({"messages": "hello, how are u?"}, config)
    agent.invoke({"messages": "how about XL"}, config)
    agent.invoke({"messages": "30 is enough, and i prefer silk on pants"}, config)
    agent.invoke({"messages": "I think XL is not good , switch to L plz"}, config)
    agent.invoke({"messages": "No i mean in terms of jacket, i like cotton"}, config)
    agent.invoke({"messages": "ok cotton for all"}, config)

    # get entire state/conversation history
    final_state = agent.invoke({"messages": "yes that's correct"}, config)
    for msg in final_state["messages"]:
        msg.pretty_print()

    # final suit options:
    print(f"Final state - Jacket: {final_state.get('jack_sizes', 'Not set')}")
    print(f"Final state - Pant: {final_state.get('pant_sizes', 'Not set')}")
    print(f"Final state - Material: {final_state.get('material_preference', 'Not set')}")
    print(f"Final state - Step: {final_state.get('current_step', 'Not set')}")

"""
================================ Human Message =================================

hello, how are u?
================================== Ai Message ==================================

Hello! I'm doing great, thank you for asking! I'm here to help you customize the perfect suit today.

Let's start with the first step - what jacket size would you like? We have:
- S (Small)
- M (Medium) 
- L (Large)
- XL (Extra Large)

What size works best for you?
================================ Human Message =================================

how about XL
================================== Ai Message ==================================

Perfect! XL jacket it is.

Now for step 2 - what pant size would you like? We have:
- 28
- 30
- 32
- 34

What size would work best for you?
================================ Human Message =================================

30 is enough, and i prefer silk on pants
================================== Ai Message ==================================

Great choice on the pant size 30! However, I need to clarify something important about the material.

The material choice applies to the ENTIRE suit - both the jacket AND the pants together. So if you choose silk, both pieces will be made from silk fabric. You can't have different materials for different pieces.

So to confirm: Would you like the complete suit (jacket and pants) made from silk material?
================================ Human Message =================================

I think XL is not good , switch to L plz
================================== Ai Message ==================================

No problem! I'll switch that to a Large jacket for you.

So we have:
- Jacket: L
- Pants: 30
- Material: Silk (for the complete suit)

Does this combination look good to you?
================================ Human Message =================================

No i mean in terms of jacket, i like cotton
================================== Ai Message ==================================

I understand you prefer cotton for the material, but I want to make sure we're on the same page.

The material choice applies to the ENTIRE suit - both jacket and pants together. So if you choose cotton, both the jacket AND the pants will be made from cotton fabric.

So to confirm your complete order:
- Jacket: L
- Pants: 30
- Material: Cotton (for both jacket and pants)

Is this correct?
================================ Human Message =================================

ok cotton for all
================================== Ai Message ==================================

Perfect! Let me confirm your complete suit customization:

- Jacket: L
- Pants: 30
- Material: Cotton (for the entire suit)

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

Excellent! Your suit customization has been saved. You've chosen:

- Jacket Size: L
- Pant Size: 30
- Material: Cotton

Your order is now complete. Thank you for choosing our custom suit service!
Final state - Jacket: L
Final state - Pant: 30
Final state - Material: cotton
Final state - Step: completed
"""