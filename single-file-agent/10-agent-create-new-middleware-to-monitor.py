from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pprint import pprint
# * new: use customize middleware
from langgraph.runtime import Runtime
from langchain.agents.middleware import (
    before_model,after_model,
    before_agent,after_agent,
    wrap_model_call,wrap_tool_call,
    ModelRequest,ModelResponse,
    AgentState
)

"""
There are 6 tool to customize middleware in langchain:
@dynamic_prompt - customize system prompt dynamically

@wrap_model_call - Wraps each model call with custom logic
@wrap_tool_call - Wraps each tool call with custom logic

@before_agent - Runs before agent starts (once per invocation)
@before_model - Runs before each model call
@after_model - Runs after each model response
@after_agent - Runs after agent completes (once per invocation)
"""

load_dotenv()

@before_model
def print_chat_info(state: AgentState, runtime: Runtime):
    print("=== Before Model Call ===")
    pprint(state)
    pprint(runtime)

@after_model
def print_chat_end(state: AgentState, runtime: Runtime):
    print("=== After Model Response ===")
    pprint(state)
    pprint(runtime)

llm = ChatOpenAI(model="kimi-k2")
agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    middleware=[print_chat_info, print_chat_end]  # * new: add customized middleware
)

if __name__ == "__main__":
    for state in agent.stream(
        {"messages":"Hello! Who are you?"},
        stream_mode="values"
    ):
        latest_msg = state["messages"][-1]
        latest_msg.pretty_print()

"""
================================ Human Message =================================

Hello! Who are you?
=== Before Model Call ===
{'messages': [HumanMessage(content='Hello! Who are you?', additional_kwargs={}, response_metadata={}, id='12bfd12a-2590-4248-bffa-ab80b9cbf39f')]}
Runtime(context=None,
        store=None,
        stream_writer=<function Pregel.stream.<locals>.stream_writer at 0x10a3762a0>,
        previous=None)
================================== Ai Message ==================================

Hello! I'm Kimi, a large language model trained by Moonshot AI. I'm here to help answer your questions and assist with anything you need. How can I help you today?
=== After Model Response ===
{'messages': [HumanMessage(content='Hello! Who are you?', additional_kwargs={}, response_metadata={}, id='12bfd12a-2590-4248-bffa-ab80b9cbf39f'),
              AIMessage(content="Hello! I'm Kimi, a large language model trained by Moonshot AI. I'm here to help answer your questions and assist with anything you need. How can I help you today?", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 38, 'prompt_tokens': 23, 'total_tokens': 61, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'kimi-k2', 'system_fingerprint': None, 'id': 'chat-', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--c610f4f8-2b34-431b-8df2-7276333dd38c-0', usage_metadata={'input_tokens': 23, 'output_tokens': 38, 'total_tokens': 61, 'input_token_details': {}, 'output_token_details': {}})]}
Runtime(context=None,
        store=None,
        stream_writer=<function Pregel.stream.<locals>.stream_writer at 0x10a3762a0>,
        previous=None)
"""
