from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
# * new: import SummaryMiddleWare
from langchain.agents.middleware import SummarizationMiddleware

load_dotenv()

llm = ChatOpenAI(model="kimi-k2")

# * new: create SummarizationMiddleware instance
sum_mid = SummarizationMiddleware(
    model=llm,
    max_tokens_before_summary=400,   # when the total tokens exceed this, trigger summary
    messages_to_keep=2,              # keep the last 2 messages in full
)

agent = create_agent(
    model=llm,
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),   # this is a must when using SummaryMiddleWare
    middleware=[sum_mid]            # * new: add the middleware to agent
)

config = {"configurable":{"thread_id":"summary_thread"}}

if __name__ == "__main__":
    agent.invoke({"messages": "hi, my name is bob"}, config)
    agent.invoke({"messages": "write a short poem about cats"}, config)
    agent.invoke({"messages": "now do the same but for dogs"}, config)
    state = agent.invoke({"messages": "what's my name?"}, config)

    for msg in state["messages"]:
        msg.pretty_print()
"""
================================ Human Message =================================

hi, my name is bob
================================== Ai Message ==================================

Hi Bob! Nice to meet you—how can I help you today?
================================ Human Message =================================

write a short poem about cats
================================== Ai Message ==================================

Bob, for you—a whiskered ode:

Paws like quiet commas  
step across the midnight page;  
eyes are lanterns, slit and golden,  
reading secrets in the dark.  

They curl into parentheses  
and purr the sentence of the night—  
a soft, unending clause of calm  
tucked just beneath our sleep.
================================ Human Message =================================

now do the same but for dogs
================================== Ai Message ==================================

Bob, here’s a tail-wagging stanza or two:

Dawn cracks its orange tennis ball—  
a dog explodes like laughter,  
four-footed joy ricocheting  
off porch, off sky, off heart.  

Ears flap like loose sails,  
tongue a pink flag of allegiance,  
every bound a shouted sentence  
ending in exclamation marks of mud.  

Night lowers; the dog circles once,  
curls into a comma of trust,  
and sighs the warm, dependable period  
that lets the whole day lie still.
================================ Human Message =================================

what's my name?
================================== Ai Message ==================================

Your name is Bob.
"""