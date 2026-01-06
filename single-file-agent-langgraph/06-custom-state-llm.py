from langgraph.graph import START,END,StateGraph
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv

# * new: 自定义state需要的导入
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict,List,Literal,Annotated
from pydantic import Field,BaseModel

load_dotenv('../.env')

# * new: 自定义状态
class MyState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    llm_calls: int = Field(default=5)

llm = init_chat_model('openai:kimi-k2')
def llm_node(state: MyState):
    prompt_msg = SystemMessage("你是惜字如金的小助手，每次回复都在一句话以内")
    response = llm.invoke([prompt_msg, *state.messages])
    print(response)
    new_llm_calls = state.llm_calls + 1
    return {"messages":response, "llm_calls": new_llm_calls}

# 1. 创建图
f = StateGraph(state_schema=MyState)
f.add_node('llm', llm_node)
# 加边
f.add_edge(START,'llm')
f.add_edge('llm', END)
# 编译
agent = f.compile()

if __name__ == "__main__":
    # 简单调用模型，注意这个模型并不会像langchain create agent一样看到其他state字段
    state = agent.invoke({"messages":["你是什么模型？"]})
    print(f'llm_calls: {state["llm_calls"]}')
    state["messages"][-1].pretty_print()
    """
    llm_calls: 6
================================== Ai Message ==================================

我是Qwen，由阿里云研发的大规模语言模型。...
    """