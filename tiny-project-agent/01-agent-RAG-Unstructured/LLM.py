import os
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

chat_llm = ChatOpenAI(
    model=os.getenv("CHAT_MODEL"),
    api_key=os.getenv("CHAT_MODEL_API_KEY"),  # local deploy model
    base_url=os.getenv("BASE_URL"),
)

vl_llm = ChatOpenAI(
    model=os.getenv("VL_MODEL"),
    api_key=os.getenv("VL_MODEL_API_KEY"),  # local deploy model
    base_url=os.getenv("BASE_URL"),
)

embed_llm = OpenAIEmbeddings(
    model=os.getenv("EMBED_MODEL"),
    api_key=os.getenv("EMBED_MODEL_API_KEY"),  # local deploy model
    base_url=os.getenv("BASE_URL"),
    check_embedding_ctx_length=False,  # Must !!!
    chunk_size=20,  # batch process documents 's embed and store
)


if __name__ == "__main__":
    print(chat_llm.model_name) # ministral-3-3b-instruct-2512
    print(chat_llm.openai_api_base) # http://127.0.0.1:1234/v1/