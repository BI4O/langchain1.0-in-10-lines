from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, MessagesState, StateGraph
from dotenv import load_dotenv

load_dotenv('../.env')
llm = init_chat_model('openai:kimi-k2')

# 没有自定义state就要传入一个基本的MsgState
async def mock_llm(state: MessagesState):
  system_message = SystemMessage("You are a helpful assistant.")
  response = await llm.ainvoke(
    [
      system_message,
      *state["messages"],
    ]
  )
  return {"messages": response}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
agent = graph.compile()

if __name__ == "__main__":
    import asyncio
    state = asyncio.run(agent.ainvoke({"messages":["hi"]}))
    state["messages"][-1].pretty_print()
    """
================================== Ai Message ==================================

Hi there! 😊 How can I assist you today? Whether you have a question, need help with something, or just want to chat, I'm here for you!
    """