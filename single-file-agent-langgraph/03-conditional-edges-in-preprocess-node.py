from typing import TypedDict, Annotated, Literal
from langgraph.graph import START, END, StateGraph
import operator
from langgraph.types import Command # intergrate logic in node

# 1.define state
class State(TypedDict):
    messages: Annotated[list[str], operator.add]

# 2.define nodes
# 如果你不指定返回类型里面连接的节点结果，画图就不会画出来
def preprocess_node(state: State) -> Command[Literal['left', 'right', END]]:
    """Preprocess the messages by adding a greeting."""
    print(f"preprocess got state decision: {state['messages'][-1]}")
    next: Literal['left', 'right', END]
    match state['messages'][-1]:
        case 'l':
            next = 'left'
        case 'r':
            next = 'right'
        case _:
            next = END
    return Command(update=State(messages=["done"]),goto=next)

def left_node(state: State) -> State:
    print(f"left node got state: {state}")
    return State(messages=["go left success!"])

def right_node(state: State) -> State:
    print(f"right node got state: {state}")
    return State(messages=["go right success!"])


# 3.draw graph
bdr = StateGraph(State) # 定义类型
bdr.add_node('preprocess', preprocess_node) # 添加节点
bdr.add_node('left', left_node) # 添加节点
bdr.add_node('right', right_node) # 添加节点

bdr.add_edge(START, 'preprocess') # 添加边
bdr.add_edge('left', END)
bdr.add_edge('right', END)

# 4.compile
agent = bdr.compile()

if __name__ == "__main__":
    # 根据输入来决定走哪条路
    state = agent.invoke(State(messages=[input("Enter command (l/r): ")]))
    print(f'result state: {state}')

    # 画asccii
    print(agent.get_graph().draw_ascii())

    """
Enter command (l/r): l
preprocess got state decision: l
left node got state: {'messages': ['l', 'done']}
result state: {'messages': ['l', 'done', 'go left success!']}
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


