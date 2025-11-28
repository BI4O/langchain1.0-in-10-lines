from langchain.agents import create_agent
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool
from dotenv import load_dotenv

# for embedding doc
import bs4
from langchain_community.document_loaders import WebBaseLoader

# pip install langchain langchain-text-splitters langchain-community bs4

# 1. load llm
load_dotenv()
chat_llm = ChatOpenAI(model="kimi-k2")
embed_llm = OpenAIEmbeddings(
    model="text-embedding-qwen3-embedding-0.6b",
    api_key="not-needed",  # local deploy model
    base_url="http://127.0.0.1:1234/v1/",
    check_embedding_ctx_length=False,  # Must !!!
    chunk_size=5  # batch process documents 's embed and store
)
# 2. init store provider, use memory for demo
vector_store = InMemoryVectorStore(embed_llm)

# 3.1 Load document
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",), # can add more here
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()
assert len(docs) == 1
print(f"Load doc total characters: {len(docs[0].page_content)}") # 43047

# 3.2 split document(s)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)
print(f"Split blog post into {len(all_splits)} sub-documents.") # 63

# 3.3 model embed splited-docs and store
document_ids = vector_store.add_documents(documents=all_splits)
print(document_ids[:3])

# 4. define retrival tool
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# 5. create agent
agent = create_agent(
    model=chat_llm,
    system_prompt="You are a helpful assitant, Use the tool to help answer user queries.",
    tools=[retrieve_context]
)

if __name__ == "__main__":
    for state in agent.stream(
        {"messages":"What is the standard method for Task Decomposition?"},
        stream_mode="values"
    ):
        state["messages"][-1].pretty_print()

"""
Load doc total characters: 43047
Split blog post into 34 sub-documents.
['179d368a-78c6-4366-b825-b06ddd513b09', 'a4b86c70-5bbe-4e35-bf6e-ac3143f37453', '0494cced-031e-4780-829e-a2494b9d0505']
================================ Human Message =================================

What is the standard method for Task Decomposition?
================================== Ai Message ==================================
Tool Calls:
  retrieve_context (retrieve_context:0)
 Call ID: retrieve_context:0
  Args:
    query: standard method for Task Decomposition
================================= Tool Message =================================
Name: retrieve_context

Source: {'source': 'https://lilianweng.github.io/posts/2023-06-23-agent/', 'start_index': 30104}
Content: You should only respond in JSON format as described below
Response Format:
{
    "thoughts": {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    },
    "command": {
        "name": "command name",
        "args": {
            "arg name": "value"
        }
    }
}
Ensure the response can be parsed by Python json.loads
GPT-Engineer is another project to create a whole repository of code given a task specified in natural language. The GPT-Engineer is instructed to think over a list of smaller components to build and ask for user input to clarify questions as needed.
Here are a sample conversation for task clarification sent to OpenAI ChatCompletion endpoint used by GPT-Engineer. The user inputs are wrapped in {{user input text}}.
[
  {
    "role": "system",
    "content": "You will read instructions and not carry them out, only seek to clarify them.\nSpecifically you will first summarise a list of super short bullets of areas that need clarification.\nThen you will pick one clarifying question, and wait for an answer from the user.\n"
  },
  {
    "role": "user",
    "content": "We are writing {{a Super Mario game in python. MVC components split in separate files. Keyboard control.}}\n"
  },
  {
    "role": "assistant",
    "content": "Summary of areas that need clarification:\n1. Specifics of the Super Mario game (e.g. level design, characters, gameplay mechanics)\n2. Details about the MVC components (e.g. which components are in each file)\n3. Keyboard control implementation (e.g. which keys to use, how to handle input)\n\nClarifying question:\nCan you provide more details about the Super Mario game, such as level design, characters, and gameplay mechanics?"
  },
  {
    "role": "user",

Source: {'source': 'https://lilianweng.github.io/posts/2023-06-23-agent/', 'start_index': 17352}
Content: Illustration of how HuggingGPT works. (Image source: Shen et al. 2023)

The system comprises of 4 stages:
(1) Task planning: LLM works as the brain and parses the user requests into multiple tasks. There are four attributes associated with each task: task type, ID, dependencies, and arguments. They use few-shot examples to guide LLM to do task parsing and planning.
Instruction:

The AI assistant can parse user input to several tasks: [{"task": task, "id", task_id, "dep": dependency_task_ids, "args": {"text": text, "image": URL, "audio": URL, "video": URL}}]. The "dep" field denotes the id of the previous task which generates a new resource that the current task relies on. A special tag "-task_id" refers to the generated text image, audio and video in the dependency task with id as task_id. The task MUST be selected from the following options: {{ Available Task List }}. There is a logical relationship between tasks, please note their order. If the user input can't be parsed, you need to reply empty JSON. Here are several cases for your reference: {{ Demonstrations }}. The chat history is recorded as {{ Chat History }}. From this chat history, you can find the path of the user-mentioned resources for your task planning.

(2) Model selection: LLM distributes the tasks to expert models, where the request is framed as a multiple-choice question. LLM is presented with a list of models to choose from. Due to the limited context length, task type based filtration is needed.
Instruction:

Given the user request and the call command, the AI assistant helps the user to select a suitable model from a list of models to process the user request. The AI assistant merely outputs the model id of the most appropriate model. The output must be in a strict JSON format: "id": "id", "reason": "your detail reason for the choice". We have a list of models for you to choose from {{ Candidate Models }}. Please select one model from the list.
================================== Ai Message ==================================

The standard method for Task Decomposition is to have an LLM (acting as the “brain”) parse a high-level user request into a set of smaller, well-defined sub-tasks.  
Each sub-task is annotated with four attributes:

1. Task type  
2. Unique task ID  
3. Dependencies (which earlier tasks it needs outputs from)  
4. Arguments (text, image, audio, video, etc. that the task operates on)

This parsing is done with few-shot prompting: the LLM is shown a short list of demonstration examples so it learns the required JSON format and the allowed task types.  
Once the decomposition is produced, the system can schedule and execute the sub-tasks in the correct dependency order, often distributing them to specialized models or tools.
"""


