from typing import TypedDict, Annotated, Literal
from langgraph.graph import START, END, StateGraph
import operator

# 1.define state
class State(TypedDict):
    messages: Annotated[list[str], operator.add]

# 2.define nodes
def preprocess_node(state: State):
    """Preprocess the messages by adding a greeting."""
    print(f"preprocess got state decision: {state['messages'][-1]}")
    return

def left_node(state: State) -> State:
    print(f"left node got state: {state}")
    return State(messages=["go left success!"])

def right_node(state: State) -> State:
    print(f"right node got state: {state}")
    return State(messages=["go right success!"])

# 3. define conditional edge function
def conditional_edge(state: State) -> Literal['left', 'right', END]:
    """Decide which path to take based on the last message."""
    match state['messages'][-1]:
        case 'l':
            return 'left'
        case 'r':
            return 'right'
        case _:
            return END

# 4.draw graph
bdr = StateGraph(State) # 定义类型
bdr.add_node('preprocess', preprocess_node) # 添加节点
bdr.add_node('left', left_node) # 添加节点
bdr.add_node('right', right_node) # 添加节点

bdr.add_edge(START, 'preprocess') # 添加边
bdr.add_conditional_edges('preprocess', conditional_edge) # 添加条件多边，注意有s
bdr.add_edge('left', END)
bdr.add_edge('right', END)

# 5.compile
agent = bdr.compile()

if __name__ == "__main__":
    # 根据输入来决定走哪条路
    state = agent.invoke(State(messages=[input("Enter command (l/r): ")]))
    print(f'result state: {state}')

    # 画asccii
    print(agent.get_graph().draw_ascii())

    """
preprocess got state decision: r
right node got state: {'messages': ['r']}
result state: {'messages': ['r', 'go right success!']}
               +-----------+             
               | __start__ |             
               +-----------+             
                     *                   
                     *                   
                     *                   
              +------------+             
              | preprocess |             
              +------------+.            
            ..       .       ...         
         ...         .          ..       
       ..            .            ...    
+------+        +-------+            ..  
| left |*       | right |         ...    
+------+ ***    +-------+       ..       
            **       *       ...         
              ***    *    ...            
                 **  *  ..               
                +---------+              
                | __end__ |              
                +---------+              
    """
    
    