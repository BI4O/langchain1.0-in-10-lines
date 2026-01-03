from typing import TypedDict, Annotated
import operator
from langgraph.graph import START, END, StateGraph

# 1.define state
# 不一样的是这次加上了reducer，表示经过node的时候
# 无论node返回什么，都根据reducer来append这些内容，而不是取代
class State(TypedDict):
    messages: Annotated[list[str], operator.add]

# 2.define nodes
def left_one(state: State) -> State:
    print(f"left one got state: {state}")
    return State(messages=["L1"])

def left_two(state: State) -> State:
    print(f"left two got state: {state}")
    return State(messages=["L2"])

def right_one(state: State) -> State:
    print(f"right one got state: {state}")
    return State(messages=["R1"])

def right_two(state: State) -> State:
    print(f"right two got state: {state}")
    return State(messages=["R2"])

# 3.define graph
bdr = StateGraph(State) # 定义类型
bdr.add_node('left_one', left_one) # 添加节点
bdr.add_node('left_two', left_two) # 添加节点
bdr.add_node('right_one', right_one) # 添加节点
bdr.add_node('right_two', right_two) # 添加节点

bdr.add_edge(START, 'left_one') # 添加边
bdr.add_edge(START, 'right_one') # 添加边
bdr.add_edge('left_one', 'left_two') # 添加边
bdr.add_edge('right_one', 'right_two') # 添加边
bdr.add_edge('left_two', END) # 添加边
bdr.add_edge('right_two', END) # 添加边

agent = bdr.compile()

if __name__ == "__main__":
    state = agent.invoke(State(messages=["start"]))
    print(f'result state: {state}')

    # 画asccii
    print(agent.get_graph().draw_ascii())
    
    """
left one got state: {'messages': ['start']}
right one got state: {'messages': ['start']}
left two got state: {'messages': ['start', 'L1', 'R1']}
right two got state: {'messages': ['start', 'L1', 'R1']}
result state: {'messages': ['start', 'L1', 'R1', 'L2', 'R2']}
           +-----------+              
           | __start__ |              
           +-----------+              
           ***         ***            
          *               *           
        **                 **         
+----------+           +-----------+  
| left_one |           | right_one |  
+----------+           +-----------+  
      *                       *       
      *                       *       
      *                       *       
+----------+           +-----------+  
| left_two |           | right_two |  
+----------+           +-----------+  
           ***         ***            
              *       *               
               **   **                
            +---------+               
            | __end__ |               
            +---------+                    
    """