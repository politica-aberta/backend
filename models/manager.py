from llama_index.agent import ParallelAgentRunner
from llama_index.agent.openai.step import OpenAIAgentWorker
from llama_index.llms.base import ChatMessage

from llama_index.tools import QueryEngineTool
from constants import SYSTEM_PROMPT_MULTI_PARTY

class PoliticalPartyManager:
    def __init__(self, llm=None):
        self.political_parties: dict = {}
        self.multi_party_agent = None
        self.llm = llm

    def insert(self, political_party):
        name = political_party.name

        if name in self.political_parties:
            raise ValueError("Political party name already exists")

        self.political_parties[name] = political_party

    def get(self, party_name):
        if party_name not in self.political_parties:
            raise ValueError("Political party name does not exist")
        return self.political_parties[party_name]

    def get_all(self):
        return self.political_parties.values()

    def delete(self, party_name):
        if party_name not in self.political_parties:
            raise ValueError("Political party name does not exist")
        del self.political_parties[party_name]

    def __del__(self):
        self.political_parties.clear()

    def generate_multi_party_agent(self, parties: list[str] | None = None):
        if parties is None:
            parties = list(self.political_parties.keys())
        all_tools: list[QueryEngineTool] = []
        for p in parties:
            # define tools
            if not self.political_parties[p].tool:
                raise Exception("no tool for " + p)
            all_tools.append(self.political_parties[p].tool)


        agent_worker = OpenAIAgentWorker.from_tools(
            tools=all_tools,
            llm=self.llm,
            max_function_calls=8,
            prefix_messages=[
                ChatMessage(content=SYSTEM_PROMPT_MULTI_PARTY, role="system")
            ],
        )

        self.multi_party_agent = ParallelAgentRunner(
            agent_worker=agent_worker,
            llm=self.llm,
        )
