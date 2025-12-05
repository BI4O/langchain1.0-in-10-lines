from langchain.agents import create_agent
from langchain.tools import tool
from CustomConverter import converter
from CustomVectorDB import init_vector_database
from LLM import chat_llm, embed_llm
import os

# install first: uv add langchain-docling langchain_openai langchain_text_splitters

# config
def get_raw_docs_paths(dpath='./docs'):
    return [os.path.join(dpath, i) for i in os.listdir(dpath)]

# 1. init vector database
vdb = init_vector_database("chroma_db", embed_llm=embed_llm)
print(f"vector database loaded {vdb._collection.count()} pieces sub-chunks")

# 2. define retrieve tool
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    print("tool search keyword", query)
    retrieved_docs = vdb.similarity_search(query, k=int(os.getenv("RETRIVE_TOP_N"))) # retrive n most related docs
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# 3. create agent
agent = create_agent(
    model=chat_llm,
    system_prompt="You are an AI assistant for Sunshine Breakfast Foods Co., Ltd. \
        Your company was founded in 2015, headquartered in Beijing, \
        specializing in high-quality breakfast foods with 5 production bases and 200+ chain stores. \
        Your main products include bakery series, beverage series, ready-to-eat series, and nutrition series. \
        IMPORTANT: Always use the retrieve_context tool to find accurate information \
        from company documents before answering any questions about \
        company details, contact information, products, or services. \
        Never make up contact information or company details.",
    tools=[retrieve_context]
)

if __name__ == "__main__":
    import re

    print("🤖 RAG Robot start, type 'quit' to quit")
    while True:
        ask = input("\n🙋 Me: ").strip()
        if ask.lower() in ['quit', 'exit', 'bye']: break
        print("🤖 Robot: ", end="", flush=True)
        for token, metadata in agent.stream({"messages": ask}, stream_mode="messages"):
            node = metadata.get("langgraph_node", "")
            # extract used file
            if node == "tools" and token.content:
                chunks = re.split("\n\n", token.content)
                files = [re.search("'source': './docs/(.*?)'", i).group(1) for i in chunks]
                contents = [re.search("Content: ([\s\S]*)", i).group(1) for i in chunks]
                for i,(f,c) in enumerate(zip(files,contents)):
                    print(f"\n===== Search file {i+1}: {f} =====")
                    print(f"Content: {c}")
            # print response
            elif node == "model" and token.content:               
                print(token.content, end="", flush=True)
        print()  

"""
🙋 Me: 我们公司的牛奶多少钱
🤖 Robot: 2025-12-04 22:04:39,871 - INFO - HTTP Request: POST http://127.0.0.1:1234/v1/chat/completions "HTTP/1.1 200 OK"
为了提供准确的牛奶价格信息，我需要查询公司内部的相关资料。请稍等，我将为您查找具体的价格详情。

tool search keyword 公司牛奶产品的价格
2025-12-04 22:04:43,003 - INFO - HTTP Request: POST http://127.0.0.1:1234/v1/embeddings "HTTP/1.1 200 OK"

===== Search file 1: product_catalog.pdf =====
Content: Sunshine Breakfast Foods - Product Catalog
Beverage Series
Pure Milk, Price = $6.99/1L. Yogurt, Price = $8.99/1L. Fresh Juice, Price = $15.99/1L. Soy Milk, Price = $7.99/1L

===== Search file 2: product_catalog.pdf =====
Content: Sunshine Breakfast Foods - Product Catalog
Nutrition Series
Energy Bar, Price = $24.99/box. Mixed Nuts, Price = $32.99/bag. Oatmeal, Price = $28.99/bag. Protein Powder, Price = $89.99/can

===== Search file 3: company_profile.md =====
Content: 阳光早餐食品有限公司 - 公司简介
主要产品线
2. 饮品系列
- 纯牛奶
- 酸奶
- 果汁
- 豆浆
2025-12-04 22:04:43,053 - INFO - HTTP Request: POST http://127.0.0.1:1234/v1/chat/completions "HTTP/1.1 200 OK"
根据公司产品目录，我们公司的纯牛奶价格为 **$6.99/1L**。如果您需要其他饮品（如酸奶、果汁或豆浆）的价格，也可以告诉我！
"""