from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv

# * new mcp
from langchain_mcp_adapters.client import MultiServerMCPClient

# set OPENAI_API_KEY、OPENAI_BASE_URL environment variables before running
load_dotenv()

mcp_client = MultiServerMCPClient(
            {
                "time": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@theo.foobar/mcp-time"],
                }
            },
        )

# initialize llm
llm = ChatOpenAI(model="kimi-k2")

if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize MCP tools and agent in async context
        mcp_tools = await mcp_client.get_tools()

        agent = create_agent(
            model=llm,
            tools=mcp_tools,
            system_prompt="You are a helpful assistant."
        )

        question = "What time is it in Tokyo right now?"
        async for msg in agent.astream({"messages": question}, stream_mode="values"):
            msg["messages"][-1].pretty_print()

    asyncio.run(main())

"""
================================ Human Message =================================

What time is it in Tokyo right now?
================================== Ai Message ==================================

I'll check the current time in Tokyo for you.
Tool Calls:
  current_time (current_time:0)
 Call ID: current_time:0
  Args:
    timezone: Asia/Tokyo
================================= Tool Message =================================
Name: current_time

2025-12-03T12:52:13+09:00
================================== Ai Message ==================================

The current time in Tokyo is **12:52 PM** (12:52:13) on December 3, 2025. Tokyo is in the Japan Standard Time zone (UTC+9).
"""