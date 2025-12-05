from LLM import embed_llm
from CustomConverter import converter
from langchain_chroma import Chroma
from langchain_docling import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def get_raw_docs_paths(dpath='./docs'):
    return [os.path.join(dpath, i) for i in os.listdir(dpath)]

def init_vector_database(directory, embed_llm):
    vector_store = Chroma(
        collection_name="db1",
        embedding_function=embed_llm,
        persist_directory=directory,
    )
    return vector_store

def load_raw_docs_and_split(docs_path, converter):
    loader = DoclingLoader(docs_path, converter=converter)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents.")

    # define spliter and split document(s)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # 增大chunk size到8000字符
        chunk_overlap=100,  # 相应增大overlap
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_documents(docs)
    print(f"Split documents into {len(all_splits)} sub-documents.")
    return all_splits

def crate_vector_database(docs_path, name="chroma_db"):
    # 如果这个数据库已经有了，那
    if os.path.isdir(name):
        print(f"{name} database already exists !!")
        return
    # 数据处理
    split_docs = load_raw_docs_and_split(docs_path, converter)
    for doc in split_docs:
        # 只保留source字段，删除复杂的dl_meta
        doc.metadata = {
            'source': doc.metadata.get('source', 'unknown')
        }
    # 初始化空数据库
    db = init_vector_database(name, embed_llm)
    print(f"数据库容量加载前容量：{db._collection.count()}")
    # 加载数据
    db.add_documents(split_docs)
    print(f"数据库容量加载后容量：{db._collection.count()}")

def vector_database_add_docs(name, docs):
    if not os.path.isdir(name):
        print(f"{name} database is not existing !!")
        return
    # 数据处理
    split_docs = load_raw_docs_and_split(docs_path, converter)
    for doc in split_docs:
        # 只保留source字段，删除复杂的dl_meta
        doc.metadata = {
            'source': doc.metadata.get('source', 'unknown')
        }
    # 初始化空数据库
    db = init_vector_database(name, embed_llm)
    print(f"数据库容量加载前容量：{db._collection.count()}")
    # 加载数据
    db.add_documents(split_docs)
    print(f"数据库容量加载后容量：{db._collection.count()}")

if __name__ == "__main__":
    # create vector databas (should run once !!!!!)
    # files = get_raw_docs_paths()
    # crate_vector_database(files, "chroma_db")

    # test vector database
    db = init_vector_database("chroma_db", embed_llm)
    res = db.similarity_search("主要竞争对手的市场份额怎么样？", k=5)
    for i,r in enumerate(res):
        print(f"==== chunk {i + 1} from {r.metadata['source']}====")
        print(r.page_content)



