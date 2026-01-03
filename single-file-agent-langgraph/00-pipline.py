"""
[start] -> (node) -> [end]
以上是一个简单的三个节点的graph
三个概念
1. 节点node, 一个函数，接受state，返回state
2. 状态state，一个class，继承TypedDict
3. 边edge
"""
from typing import TypedDict
from langgraph.graph import START, END, StateGraph

# 1.define state
class MyState(TypedDict):
    messages: list[str]

# 2.define node
def hello_node(state: MyState) -> MyState:
    print(f"get state: {state}")
    return MyState(messages=["hello world"])

# 3.define graph
bdr = StateGraph(MyState) # 定义类型
bdr.add_node('hello', hello_node) # 添加节点
bdr.add_edge(START, 'hello') # 添加边
bdr.add_edge('hello', END) # 添加边
agent = bdr.compile()

if __name__ == "__main__":
    # 这里的messages就算你写了str，也会自动帮你转成list[str]
    # state = agent.invoke({"messages": "hi"}) # ok
    state = agent.invoke(MyState(messages=["hi"])) # 更推荐
    print(f'result state: {state}')

    # 画mermaid
    print(agent.get_graph().draw_mermaid())

    # 画asccii
    print(agent.get_graph().draw_ascii())
    
    """
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
  +-------+    
  | hello |    
  +-------+    
      *        
      *        
      *        
 +---------+   
 | __end__ |   
    """
