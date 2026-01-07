from langgraph.graph import START,END,StateGraph,MessagesState
from typing import TypedDict,List,Annotated
from pydantic import BaseModel,Field
import operator
import time
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage,SystemMessage
from langgraph.types import Send

from dotenv import load_dotenv
load_dotenv('../.env')

# 自定义类型，规定planer输出的格式
class Task(BaseModel):
    name: str = Field(description="name of this task")
    desc: str = Field(description="description of this task")

class Tasks(BaseModel):
    all_tasks: List[Task] = Field(description="task collections")

llm = init_chat_model('openai:kimi-k2-0905')
planner = create_agent(model=llm,response_format=Tasks)

# 自定义State
class State(TypedDict):
    topic: str
    tasks: List[Task]
    completed_tasks: Annotated[List[str], operator.add]
    final_conclusion: str

class LLMState(TypedDict):
    task: Task
    completed_tasks: Annotated[List[str], operator.add]

# 定义节点
def planner_node(s:State):
    # last_messages = s["messages"][-1]
    last_messages = s['topic'] + "\n\n请生成最多3个子任务来完成这个主题。"
    result = planner.invoke({"messages":last_messages})["structured_response"]
    return {"tasks": result.all_tasks}

def worker_node(s:LLMState):
    """并行节点要做的事情"""
    print(f"[DEBUG] Processing task: {s['task'].name}")
    # 添加延迟避免并发冲突
    time.sleep(0.5)
    # 使用简单的字符串调用，避免消息格式问题
    prompt = f"""任务名: {s['task'].name}
任务描述: {s['task'].desc}
请3句话内描述如何一步一步完成这个任务。"""
    # 添加重试逻辑
    for attempt in range(3):
        try:
            task_result = llm.invoke(prompt)
            return {"completed_tasks": [task_result.content]}
        except Exception as e:
            print(f"[RETRY] Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(1)
            else:
                raise

def conclude_node(s:State):
    """拼接接收到的完成的任务"""
    conclusion = '\n\n'.join(s['completed_tasks'])
    return {"final_conclusion":conclusion}

def planner_node_goto(s:State):
    """把State类型转化成LLMState给到各个worker"""
    return [
        Send('worker_node', {'task': t, 'completed_tasks': []}) \
            for t in s['tasks']
    ]

graph = StateGraph(State)
graph.add_node(planner_node)
graph.add_node(worker_node)
graph.add_node(conclude_node)

graph.add_edge(START, "planner_node")
graph.add_conditional_edges(
    "planner_node", planner_node_goto, ["worker_node"]
)
graph.add_edge("worker_node", "conclude_node")
graph.add_edge("conclude_node", END)

agent = graph.compile()

if __name__ == "__main__":
    # res = planner.invoke({"messages":"吃早餐分哪几步"})
    # print(res["structured_response"])
    # agent.get_graph().print_ascii()

    state = agent.invoke({"topic":"做一个关于大象放进冰箱的报告"})
    print(state["final_conclusion"])

    """
[DEBUG] Processing task: 大象选择与安全评估
[DEBUG] Processing task: 冰箱改装与容量验证
[DEBUG] Processing task: 操作流程与风险报告
[RETRY] Attempt 1 failed: Received response with null value for `choices`.
1. 先列清单：把“微型象”限定为可买到的树脂/毛绒/3D 打印模型象，记录官方标明的长×宽×高与克重。  
2. 用卷尺量自家冰箱每层搁板净深与净高，挑尺寸≤90 % 搁板空间、重量≤5 kg 的模型，确保门能关严且不会压裂玻璃。  
3. 选无毒水性漆、无锐角、无可拆卸小零件的款式，拆封后通风 24 h 再入箱，避免低温致漆面开裂或化学味污染食物。

1. 先清空冰箱，用卷尺量出内部长×宽×高，算出可用容积并与大象等效体积对比，确认理论可行。  
2. 拆下或上移所有可拆搁架/抽屉，必要时在侧壁加装快拆滑轨，插入一块可折叠扩展隔板，把大象“填充区”与仍需冷藏的小物品隔开。  
3. 把大象（泡沫模型或充气道具）推入，调整隔板位置直至门封条能完全贴合，用拉力计验证门封吸力≥厂家标称值即算通过。

先按“预处理→搬运→放置→关门”四步列出详细操作清单，并在每步同步记录温度、功率与异常现象。  
实验结束后把数据整理成含时序图表、能耗曲线和故障日志的完整报告。  
最后附一段伦理声明与用户安全使用建议，签字归档。
    """