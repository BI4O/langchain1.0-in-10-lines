from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("openai:qwen3-vl-8b-instruct", temperature=0)

agent = create_agent(llm, system_prompt="你是小助手，请友好地回答用户的问题。")

if __name__ == "__main__":
    state = agent.invoke({"messages": [{"role": "user", "content": "Hello, how are you?"}]})
    state["messages"][-1].pretty_print()