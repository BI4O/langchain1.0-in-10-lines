"""
LangGraph State Agent 示例

这是一个使用 LangGraph 构建的工具调用 Agent，支持：
- 多轮对话状态管理
- 动态工具调用
- 条件路由（决定是否使用工具）

运行示例：
    python 06-state-agent.py
"""

from typing import TypedDict, Literal, Sequence, Annotated
from langchain_core.messages import (
    BaseMessage, SystemMessage, AIMessage, ToolMessage
)
import operator
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import START,END,StateGraph
from dotenv import load_dotenv

load_dotenv('../.env')

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

@tool
def search(query: str) -> str:
    """联网搜索信息"""
    return f"关于'{query}'的搜索结果：这是模拟返回的搜索数据。"

# 全局初始化 LLM，避免重复创建
llm = init_chat_model("openai:kimi-k2-0905")
llm_with_tools = llm.bind_tools([search])

def chat_node(state: AgentState) -> AgentState:
    """聊天节点：处理用户消息并决定是否调用工具"""
    msg_with_prompt = [SystemMessage("you are a helpful assistant")] + state["messages"]
    response = llm_with_tools.invoke(msg_with_prompt)
    return {"messages": [response]}

def tool_node(state: AgentState) -> AgentState:
    """工具节点：执行 AI 决定的工具调用"""
    # 工具名称到工具对象的映射
    tools_by_name = {
        "search": search
        # 未来可以轻松添加更多工具
        # "calculator": calculator,
        # "weather": weather,
    }

    last_msg = state["messages"][-1]
    if not isinstance(last_msg, AIMessage):
        return state
    if not last_msg.tool_calls:
        return state

    response = []
    for t in last_msg.tool_calls:
        tool_name = t["name"]
        tool_args = t["args"]

        # 动态获取工具
        if tool_name not in tools_by_name:
            tool_result = f"错误：找不到工具 '{tool_name}'"
        else:
            tool = tools_by_name[tool_name]
            tool_result = tool.invoke(tool_args)

        response.append(
            ToolMessage(tool_result, tool_call_id=t["id"])
        )
    return {"messages": response}

def agent_goto(state: AgentState) -> Literal[END, 'tool']:
    """路由函数：决定下一步是结束还是调用工具"""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool"
    return END

# 构建工作流图
workflow = StateGraph(AgentState)
workflow.add_node("agent", chat_node)
workflow.add_node("tool", tool_node)

# 划定路径，起点，路线
workflow.set_entry_point("agent")
# agent作为入口，后续要么结束，要么用工具
workflow.add_conditional_edges("agent", agent_goto)
# 如果用工具了，结束后也要回来agent
workflow.add_edge("tool", "agent")

agent = workflow.compile()

if __name__ == "__main__":
    # 打印图结构
    print("=== Agent 图结构 ===")
    print(agent.get_graph().draw_ascii())
    print()

    # 测试 1: 不需要工具的对话
    print("=== 测试 1: 普通对话 ===")
    response1 = agent.invoke({
        "messages": [("user", "你好，请介绍一下你自己")]
    })
    print(response1["messages"][-1].content)
    print()

    # 测试 2: 需要调用工具的对话
    print("=== 测试 2: 调用搜索工具 ===")
    response2 = agent.invoke({
        "messages": [("user", "帮我搜索一下 LangChain 的最新版本")]
    })
    print(response2["messages"][-1].content)
    print()

    # 测试 3: 多轮对话
    print("=== 测试 3: 多轮对话 ===")
    initial_state = {"messages": [("user", "今天天气怎么样？")]}
    response3 = agent.invoke(initial_state)
    print(response3["messages"][-1].content)

    """
    === Agent 图结构 ===
        +-----------+        
        | __start__ |        
        +-----------+        
              *              
              *              
              *              
          +-------+          
          | agent |          
          +-------+          
          .        .         
        ..          ..       
       .              .      
+---------+        +------+  
| __end__ |        | tool |  
+---------+        +------+  

=== 测试 1: 普通对话 ===
你好！我是 Kimi，一个由月之暗面科技有限公司（Moonshot AI）训练的大语言模型。很高兴为你提供帮助！有什么可以帮你的吗？

=== 测试 2: 调用搜索工具 ===
很抱歉，由于搜索功能返回的是模拟数据，我无法获取到 LangChain 的最新版本号信息。

不过，我可以建议您通过以下方式获取 LangChain 的最新版本：

1. **PyPI 官网**：访问 https://pypi.org/project/langchain/ 查看最新版本
2. **GitHub 仓库**：访问 https://github.com/langchain-ai/langchain 查看发布版本
3. **官方文档**：查看 LangChain 官方文档获取版本信息
4. **pip 命令**：使用 `pip show langchain` 或 `pip index versions langchain` 查看版本

如果您需要我帮您搜索其他相关信息，请告诉我！

=== 测试 3: 多轮对话 ===
很抱歉，我无法为您提供准确的实时天气信息。建议您可以通过以下方式查询今天的天气：

1. 查看手机自带的天气应用
2. 访问天气预报网站（如中国天气网、天气通等）
3. 使用搜索引擎直接搜索"实时天气+您所在的城市名称"

如果您能告诉我您所在的具体城市，我可以帮您搜索该城市今天的天气预报信息。
    """

