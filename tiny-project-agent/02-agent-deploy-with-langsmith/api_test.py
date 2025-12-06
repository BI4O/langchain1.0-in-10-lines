import requests
from pprint import pprint
from tabulate import tabulate

# should run `langgraph dev` in tiny-project-agent/02-agent-deploy-with-langsmith before u run this

# 1. check server ok: curl 'http://127.0.0.1:2024/ok'
def check_ok():
    response = requests.get("http://127.0.0.1:2024/ok")
    print(response.status_code) # {'ok': True}

# 2. search assitant
def search_assitant():
    response = requests.post("http://127.0.0.1:2024/assistants/search",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "metadata": {},
            "graph_id": "agent",
            "name": "",
            "limit": 10,
            "offset": 0,
            "sort_by": "assistant_id",
            "sort_order": "asc",
            "select": ["assistant_id","name","description"]
        }
    )
    return response.json()

# 3. create assitant
def create_assistant(
    name, 
    model="openai:kimi-k2", 
    system_prompt="You are a professional email assistant"
):
    url = "http://localhost:2024/assistants"
    payload = {
        "graph_id": "agent",
            "config": {
                "configurable": {
                    "model": model,
                    "system_prompt": system_prompt,
                    "tools": ["send_email"]
                }
            },
            "name": "glm_assitant",
            "description": "Email assistant using GPT-4 for English emails"
      }

    response = requests.post(url, json=payload)
    resp_dict = response.json()
    assitant_id = resp_dict.get("assistant_id")
    return assitant_id, resp_dict

BASE_URL="http://127.0.0.1:2024"
class Client:
    def __init__(self, graph_id="agent"):
        self.graph_id=graph_id
        self.ok=self.check_ok()

    def check_ok(self):
        r = requests.get(f"{BASE_URL}/ok")
        return r.json()["ok"] if r.status_code==200 else False

    def show_agents(self, name_filter=""):
        r = requests.post(f"{BASE_URL}/assistants/search",
            json={
                "metadata": {},
                "graph_id": self.graph_id,
                "name": name_filter,
                "sort_by": "created_at",
                "select": ["created_at","assistant_id","name","description","metadata","context"]
            }
        )
        assert r.status_code == 200
        agents = r.json()

        # 打印表格
        self._print_agents_table(agents)

        return agents

    def _print_agents_table(self, agents):
        if not agents:
            print("No agents found.")
            return

        # 准备表格数据
        table_data = []
        for i, agent in enumerate(agents, 1):
            table_data.append([
                i,  # 序号
                agent['assistant_id'][:12] + '...',  # 显示前12个字符
                agent['name'],
                agent.get('description', 'N/A'),
                agent['metadata'].get('created_by', 'N/A'),
                agent['created_at'][:19].replace('T', ' ')  # 格式化时间
            ])

        # 打印表格
        headers = ['#', 'Assistant ID', 'Name', 'Description', 'Created By', 'Created At']
        print("\n" + tabulate(table_data, headers=headers, tablefmt='grid') + "\n")

    def get_agent(assitant_id='', assistant_no=0):
        "如果有assitant_id优先用ID，如果没有直接show之后拿第n个"
        if not assitant_id and assistant_no==0: # 都没有
            print("Should provide at least assistant_no or assitant_id")
            return
        if assistant_no != 0 and not assitant_id: # 有no没有id
            agents = self.show_agents()
            if agents and len(agents) > assistant_no - 1:
                assitant_id = agents[assistant_no - 1]['assistant_id']
                print(f"Selected assistant ID: {assitant_id}")
            else:
                print(f"Assistant #{assistant_no} not found")
                return
        # 有id
        # r = requests.get(f"{BASE_URL}/assistants/{assitant_id}")
        # assert r.status_code==200
        # pprint(r.json())
        # return r.json()
        
        
        

        
    

if __name__ == "__main__":
    # check_ok()
    # agent_id, agent_info_dict = create_assistant()
    # pprint(search_assitant())
    c = Client()
    c.show_agents()
    # c.get_agent(1)