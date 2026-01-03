from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.types import Command, interrupt
from langgraph.graph import START, END, StateGraph
from typing import Annotated, Literal, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
import os, uuid

# 1. load environment variables
load_dotenv()

# 2. define state schema
class EmailClass(TypedDict):
    intent: Literal['ask', 'bug', 'billing']
    urgency: Literal['low', 'medium', 'high']
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    # init info
    email_id: str
    sender: str
    content: str

    # processed info
    classification: EmailClass | None  # 用llm来生成分类的信息
    ticket_id: str | None
    search_results: list[str] | None
    customer_history: dict | None
    drift_response: str | None

# 3. define nodes
# step1
def read_email(state: EmailAgentState) -> EmailAgentState:
    "exatract and parse email content"
    pass

# step2 
llm = init_chat_model("openai:kimi-k2")
def classify_intent(state: EmailAgentState) -> EmailAgentState:
    "use llm to classify email intent"
    structured_llm = llm.with_structured_output(EmailClass)
    prompt = f"""Analyse this email and classify it into JSON format:

Email Content: {state['content']}
From: {state['sender']}

You MUST respond with a valid JSON object containing:
- intent: one of ["ask", "bug", "billing"]
- urgency: one of ["low", "medium", "high"]
- topic: a brief topic description
- summary: a brief summary of the email
- must reply in chinese

Example output format:
{{"intent": "billing", "urgency": "medium", "topic": "billing issue", "summary": "customer has billing problem"}}
"""
    classification = structured_llm.invoke(prompt)

    return {"classification": classification}

# step3 parallel job 1
def search_documentation(state: EmailAgentState) -> EmailAgentState:
    "simulate searching documentation based on email classification"
    # Simulate searching documentation
    try:
        search_results = [
            f"Documentation for {state['classification']['topic']}",
            f"FAQs related to {state['classification']['topic']}"
        ]
        return {"search_results": search_results}
    except Exception as e:
        return {"search_results": ["search failed : " + str(e)]}

# step3 parallel job 2
def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    "simulate creating a bug tracking ticket"
    ticket_id = f"BUG-{uuid.uuid4().hex[:8]}"
    return {"ticket_id": ticket_id}

# step4
def write_response(state: EmailAgentState) -> Command[Literal['human_review','send_reply']]:
    "generate email response draft"
    classification = state.get("classification", {})

    # init empty response
    context_sections = []
    if state.get("search_results"):
        context_sections.append("Relevant Documentation:\n" + "\n".join(state["search_results"]))
    if state.get("customer_history"):
        context_sections.append("Customer History:\n" + str(state["customer_history"]))

    # prompt to generate response
    prompt = f"""
    Draft a response to this customer email:
    {state['content']}

    Email intent: {classification.get('intent', 'N/A')}
    Urgency: {classification.get('urgency', 'N/A')}

    {chr(10).join(context_sections)}
    """

    response = llm.invoke(prompt)

    # decide next step based on urgency
    goto: Literal['human_review','send_reply']
    if classification.get("urgency") == "high":
        goto = 'human_review'
    else:
        goto = 'send_reply'
    return Command(update={"drift_response": response}, goto=goto)

# step5
def human_review(state: EmailAgentState) -> Command[Literal['send_reply',END]]:
    "human review using interrupt"
    classification = state.get("classification", {})

    # review info
    decision = interrupt({
        "email_id": state["email_id"],
        "content": state["content"],
        "urgency": classification.get("urgency", "N/A"),
        "draft_response": state.get("drift_response", ""),
        "action": "Please review and approve/reject the drafted response."
    })

    if decision.get("approved"):
        return Command(update={"drift_response": state.get("drift_response", "")}, goto='send_reply')
    else:
        return Command(update={}, goto=END)

# step6
def send_reply(state: EmailAgentState) -> Command[END]:
    "simulate sending email reply"
    print("====== send reply node working ======\n")
    print(f"Sending email reply for Email ID {state['email_id']}:\n")
    print(f"Reply: {state.get('drift_response', '')}")
    return Command(update={}, goto=END)

# 4. define graph
bdr = StateGraph(EmailAgentState)

bdr.add_node('read_email', read_email)
bdr.add_node('classify_intent', classify_intent)
bdr.add_node('search_documentation', search_documentation)
bdr.add_node('bug_tracking', bug_tracking)
bdr.add_node('write_response', write_response)
bdr.add_node('human_review', human_review)
bdr.add_node('send_reply', send_reply)

bdr.add_edge(START, 'read_email')
bdr.add_edge('read_email', 'classify_intent')
bdr.add_edge('classify_intent', 'search_documentation')
bdr.add_edge('classify_intent', 'bug_tracking')
bdr.add_edge('search_documentation', 'write_response')
bdr.add_edge('bug_tracking', 'write_response')

bdr.add_edge('send_reply', END)

checkpointer = InMemorySaver()
workflow = bdr.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    from pprint import pprint
    # print(workflow.get_graph().draw_ascii())

    # simulate invoking the email agent
    initial_state = EmailAgentState(
        email_id="EMAIL-12345",
        sender="123@qq.com",
        content="问一下账单什么时候出？"
    )

    config = {"configurable": {"thread_id": "email_thread_1"}}
    final_state = workflow.invoke(initial_state, config=config)
    print("="*60)
    print("Final state:")
    pprint(final_state, width=100, compact=False)

    """
====== send reply node working ======

Sending email reply for Email ID EMAIL-12345:

Reply: content='Subject: 账单出具时间说明\n\n您好，\n\n感谢来信询问。\n\n账单一般在每月 1 日生成，若遇节假日则顺延至下一工作日。届时系统会自动将账单发送至您预留的邮箱，并同步更新在「我的账户—账单中心」，您可随时下载查看。\n\n如需提前获取或补打历史账单，可直接在「账单中心」操作，或联系在线客服，我们会第一时间为您处理。\n\n如有其他疑问，欢迎随时与我们联系！\n\n祝好  \n客户支持团队' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 102, 'prompt_tokens': 59, 'total_tokens': 161, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'kimi-k2', 'system_fingerprint': None, 'id': 'chatcmpl-69590e676d1b90a78b11dcfc', 'finish_reason': 'stop', 'logprobs': None} id='lc_run--019b83e0-441e-7b50-9e61-f70ba889a48d-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 59, 'output_tokens': 102, 'total_tokens': 161, 'input_token_details': {}, 'output_token_details': {}}
============================================================
Final state:
{'classification': {'intent': 'billing',
                    'summary': '客户询问账单出具时间',
                    'topic': '账单出具时间',
                    'urgency': 'medium'},
 'content': '问一下账单什么时候出？',
 'drift_response': AIMessage(content='Subject: 账单出具时间说明\n\n您好，\n\n感谢来信询问。\n\n账单一般在每月 1 日生成，若遇节假日则顺延至下一工作日。届时系统会自动将账单发送至您预留的邮箱，并同步更新在「我的账户—账单中心」，您可随时下载查看。\n\n如需提前获取或补打历史账单，可直接在「账单中心」操作，或联系在线客服，我们会第一时间为您处理。\n\n如有其他疑问，欢迎随时与我们联系！\n\n祝好  \n客户支持团队', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 102, 'prompt_tokens': 59, 'total_tokens': 161, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai', 'model_name': 'kimi-k2', 'system_fingerprint': None, 'id': 'chatcmpl-69590e676d1b90a78b11dcfc', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019b83e0-441e-7b50-9e61-f70ba889a48d-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 59, 'output_tokens': 102, 'total_tokens': 161, 'input_token_details': {}, 'output_token_details': {}}),
 'email_id': 'EMAIL-12345',
 'search_results': ['Documentation for 账单出具时间', 'FAQs related to 账单出具时间'],
 'sender': '123@qq.com',
 'ticket_id': 'BUG-48e7b748'}
    """
