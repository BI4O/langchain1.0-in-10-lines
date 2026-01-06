import asyncio
from langgraph.graph import START,END,StateGraph
from pydantic import BaseModel,Field
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from dotenv import load_dotenv
load_dotenv('../.env')

# state
class State(BaseModel):
    keyword: str = Field('unknow', description='user provided keyword')
    joke: str = Field('somejoke')
    story: str = Field('somestory')
    poem: str = Field('somepoem')
    combine: str = Field('combined text')

# llm and llm nodes
llm = init_chat_model('openai:kimi-k2')
async def worker1(s:State) -> State:
    """generate joke"""
    prompt = SystemMessage(f'Use {s.keyword} to make a one-line joke')
    return {'joke': (await llm.ainvoke([prompt])).content}

async def worker2(s:State) -> State:
    """generate story"""
    prompt = SystemMessage(f'Use {s.keyword} to make a one-line story')
    return {'story': (await llm.ainvoke([prompt])).content}

async def worker3(s:State) -> State:
    """generate poem"""
    prompt = SystemMessage(f'Use {s.keyword} to make a one-line poem')
    return {'poem': (await llm.ainvoke([prompt])).content}

def aggregator(state: State):
    """Combine the joke, story and poem into a single output"""
    combined = f"Here's a story, joke, and poem about {state.keyword}!\n\n"
    combined += f"STORY:\n{state.story}\n\n"
    combined += f"JOKE:\n{state.joke}\n\n"
    combined += f"POEM:\n{state.poem}"
    return {"combine": combined}


graph = StateGraph(State)
graph.add_node(worker1)
graph.add_node(worker2)
graph.add_node(worker3)
graph.add_node(aggregator)

graph.add_edge(START,'worker1')
graph.add_edge(START,'worker2')
graph.add_edge(START,'worker3')
graph.add_edge('worker1','aggregator')
graph.add_edge('worker2','aggregator')
graph.add_edge('worker3','aggregator')
graph.add_edge('aggregator',END)

agent = graph.compile()

if __name__ == "__main__":
    agent.get_graph().print_ascii()
    state = asyncio.run(agent.ainvoke({"keyword": "cats"}))
    print(state['combine'])
    """
                     +-----------+                       
                     | __start__ |                       
                   **+-----------+***                    
               ****         *        ****                
           ****             *            ****            
         **                 *                **          
+---------+           +---------+           +---------+  
| worker1 |           | worker2 |           | worker3 |  
+---------+****       +---------+        ***+---------+  
               ****         *        ****                
                   ****     *    ****                    
                       **   *  **                        
                    +------------+                       
                    | aggregator |                       
                    +------------+                       
                            *                            
                            *                            
                            *                            
                      +---------+                        
                      | __end__ |                        
                      +---------+                        
Here's a story, joke, and poem about cats!

STORY:
The cat leapt onto the windowsill, tail flicking like a metronome counting down to the storm's first drop.

JOKE:
I tried to train my cat to do tricks, but she just gave me a blank stare and knocked the clicker off the table—turns out *I’m* the one getting schooled.

POEM:
A cat, tail curled like a question mark, purrs the answer to silence.
    """


