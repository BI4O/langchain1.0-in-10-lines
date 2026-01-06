from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, MessagesState, StateGraph
from dotenv import load_dotenv
from langchain.tools import tool # * new
from langgraph.prebuilt import ToolNode

load_dotenv('../.env')

# ===== 构建 tool node =====
@tool
def get_weather(city:str) -> str:
    "get weather of a city"
    return f"the weather in {city} is sunny!"

@tool
def greet() -> str:
    "greeting"
    return "hello there"

tool_node = ToolNode([get_weather,greet])

# ===== 构建 chat node =====
llm = init_chat_model('openai:kimi-k2').bind_tools([get_weather,greet])
# 没有自定义state就要传入一个基本的MsgState
async def llm_node(state: MessagesState) -> MessagesState:
    system_message = SystemMessage("You are a helpful assistant.")
    it = [system_message,*state["messages"]]
    print(f"DEBUG: 实际发给 AI 的消息流: {[type(m).__name__ for m in it]}")
    response = await llm.ainvoke(
        it
    )
    return {"messages": [response]}

# ===== 组装 graph =====
graph = StateGraph(MessagesState)
graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "llm")
# graph.add_edge("llm", END)
graph.add_conditional_edges(
    'llm', 
    lambda state: 'tools' if state["messages"][-1].tool_calls else END,
    ['tools',END]
)
graph.add_edge("tools","llm") # * new
agent = graph.compile()

if __name__ == "__main__":
    import asyncio
    state = asyncio.run(agent.ainvoke({"messages":["hi"]}))
    # state["messages"][-1].pretty_print()
    print([m.content for m in state["messages"]])
    state = asyncio.run(agent.ainvoke({"messages":state["messages"] + ["check SZ weather"]}))
    print([m.content for m in state["messages"]])

    """
DEBUG: 实际发给 AI 的消息流: ['SystemMessage', 'HumanMessage']
['hi', 'Hello! How can I help you today?']
DEBUG: 实际发给 AI 的消息流: ['SystemMessage', 'HumanMessage', 'AIMessage', 'HumanMessage']
DEBUG: 实际发给 AI 的消息流: ['SystemMessage', 'HumanMessage', 'AIMessage', 'HumanMessage', 'AIMessage', 'ToolMessage']
['hi', 
'Hello! How can I help you today?', 
'check SZ weather', 
"I'll check the weather for Shenzhen (SZ).", 
'the weather in Shenzhen is sunny!', 
'Great news! The weather in Shenzhen is sunny today.']
    """