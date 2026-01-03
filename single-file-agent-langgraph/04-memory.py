"""
LangGraph 核心概念：State、Checkpoint、Thread
================================================

1. STATE（状态）= 图片（某一帧）
   - Graph 在某个时刻的完整数据快照
   - 包含所有节点间传递的信息
   - 每次节点执行后都会产生新的 state
   示例: State = {"messages": ["hello"], "user_id": 123}

2. CHECKPOINT（检查点）= 视频（一系列帧的历史记录）
   - 保存 state 的历史版本序列
   - 可以回溯到任意 checkpoint（时间旅行）
   - 支持 replay（重放）、rewind（倒退）
   示例:
     Checkpoint 1: {"messages": ["start"]}
     Checkpoint 2: {"messages": ["start", "hello"]}
     Checkpoint 3: {"messages": [...], "result": "done"}

3. THREAD（线程）= 不同的电影（独立的会话容器）
   - 隔离不同用户/会话的状态
   - 每个 thread 有独立的 checkpoint 序列
   - 类似聊天记录中的"会话 ID"
   示例:
     Thread "alice": checkpoint_1 → checkpoint_2 → ...
     Thread "bob":   checkpoint_1 → checkpoint_2 → ...
     （两者完全独立，互不干扰）

类比总结
--------
   概念        | 你的类比         | 技术含义
   ------------|------------------|----------------------
   State       | 图片（某一帧）    | 单一时间点的数据快照
   Checkpoint  | 视频（帧序列）    | State 的时间序列历史记录
   Thread      | 不同的电影        | 隔离不同会话的容器

"""

from langgraph.checkpoint.memory import InMemorySaver
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
memory = InMemorySaver()
agent = bdr.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    while True:
        input_text = input("Enter command (l/r/q): ")
        if input_text == "q":
            break
        input_state = State(messages=[input_text])
        state = agent.invoke(input_state, config=config)
        print(f'result state: {state}')

    """
Enter command (l/r/q): l
preprocess got state decision: l
left node got state: {'messages': ['l', 'done']}
result state: {'messages': ['l', 'done', 'go left success!']}
Enter command (l/r/q): r
preprocess got state decision: r
right node got state: {'messages': ['l', 'done', 'go left success!', 'r', 'done']}
result state: {'messages': ['l', 'done', 'go left success!', 'r', 'done', 'go right success!']}
Enter command (l/r/q): q
    """