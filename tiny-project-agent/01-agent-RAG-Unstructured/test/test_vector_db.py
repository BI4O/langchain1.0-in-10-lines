"""
测试已加载的向量数据库
"""

from MyModels import embed_llm
from langchain_chroma import Chroma
import os

def test_vector_database(db_path="chroma_db"):
    """测试向量数据库"""

    # 1. 连接到数据库
    print("=== 连接数据库 ===")
    vector_store = Chroma(
        collection_name="db1",
        embedding_function=embed_llm,
        persist_directory=db_path,
    )

    # 2. 查看数据库基本信息
    print(f"数据库路径: {db_path}")
    print(f"文档总数: {vector_store._collection.count()}")

    # 3. 获取一些样本数据
    print("\n=== 查看样本数据 ===")
    # 获取前5个文档
    sample_data = vector_store._collection.get(
        limit=5,
        include=['documents', 'metadatas']
    )

    print(f"获取到 {len(sample_data['documents'])} 个样本文档:")
    for i, (doc, metadata) in enumerate(zip(sample_data['documents'], sample_data['metadatas'])):
        print(f"\n样本 {i+1}:")
        print(f"  来源: {metadata.get('source', '未知')}")
        print(f"  内容长度: {len(doc)} 字符")
        print(f"  内容预览: {doc[:100]}...")

    # 4. 测试搜索功能
    print("\n=== 测试搜索功能 ===")

    test_queries = [
        "阳光早餐成立于哪一年？",
        "公司的主要产品有哪些？",
        "市场份额是多少？",
        "联系方式是什么？",
        "营养系列包括什么产品？"
    ]

    for query in test_queries:
        print(f"\n查询: {query}")
        results = vector_store.similarity_search(query, k=3)

        if results:
            print(f"找到 {len(results)} 个相关结果:")
            for i, doc in enumerate(results):
                print(f"\n  结果 {i+1}:")
                print(f"    来源: {doc.metadata.get('source', '未知')}")
                print(f"    内容: {doc.page_content}")
        else:
            print("  没有找到相关结果")

    # 5. 测试带分数的搜索
    print("\n=== 测试带分数的搜索 ===")
    query = "公司成立时间"
    results_with_scores = vector_store.similarity_search_with_score(query, k=3)

    print(f"查询: {query}")
    for doc, score in results_with_scores:
        print(f"\n  相似度分数: {score:.4f} (越小越相似)")
        print(f"  来源: {doc.metadata.get('source', '未知')}")
        print(f"  内容: {doc.page_content[:150]}...")

    # 6. 统计信息
    print("\n=== 统计信息 ===")
    all_data = vector_store._collection.get(include=['metadatas'])
    sources = {}
    for metadata in all_data['metadatas']:
        source = metadata.get('source', '未知')
        if '.' in source:
            file_type = source.split('.')[-1]
        else:
            file_type = 'unknown'
        sources[file_type] = sources.get(file_type, 0) + 1

    print("按文件类型统计:")
    for file_type, count in sources.items():
        print(f"  {file_type}: {count} 个文档")

    # 7. 查看collection信息
    print("\n=== Collection信息 ===")
    print(f"Collection名称: {vector_store._collection.name}")
    print(f"Collection ID: {vector_store._collection.id}")

    # 获取所有collection（如果有多个）
    try:
        client = vector_store._client
        collections = client.list_collections()
        print(f"\n数据库中所有collections:")
        for col in collections:
            print(f"  - {col.name} (ID: {col.id})")
    except:
        pass

if __name__ == "__main__":
    # 测试默认路径
    test_vector_database("chroma_db")