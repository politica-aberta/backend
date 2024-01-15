from llama_index import VectorStoreIndex
from llama_index.objects import ObjectIndex, SimpleToolNodeMapping
from llama_index.agent import FnRetrieverOpenAIAgent
from llama_index.tools import QueryEngineTool
from constants import SYSTEM_PROMPT_MULTI_PARTY, SIMILARITY_TOP_K



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
                
        tool_mapping = SimpleToolNodeMapping.from_objects(all_tools)
        obj_index = ObjectIndex.from_objects(
            all_tools,
            tool_mapping,
            VectorStoreIndex,
        )
        self.multi_party_agent = FnRetrieverOpenAIAgent.from_retriever(
            obj_index.as_retriever(similarity_top_k=3),
            system_prompt=SYSTEM_PROMPT_MULTI_PARTY,
            verbose=True,
        )
