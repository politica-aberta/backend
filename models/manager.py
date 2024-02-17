from llama_index.core.agent import ParallelAgentRunner

from openai_agent_worker import OpenAIAgentWorker
from llama_index.core.chat_engine.types import ChatMessage

from llama_index.core.callbacks import (
    CallbackManager,
    LlamaDebugHandler,

)

from llama_index.core.tools import QueryEngineTool
from constants import SYSTEM_PROMPT_MULTI_PARTY
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler


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

        llama_debug = LlamaDebugHandler(print_trace_on_end=True)

        callback_manager = CallbackManager([llama_debug])

        agent_worker = OpenAIAgentWorker.from_tools(
            tools=all_tools,
            llm=self.llm,
            # verbose=True,
            # callback_manager=callback_manager,
            max_function_calls=8,
            prefix_messages=[
                ChatMessage(content=SYSTEM_PROMPT_MULTI_PARTY, role="system")
            ],
        )

        self.multi_party_agent = ParallelAgentRunner(
            agent_worker=agent_worker,
            callback_manager=callback_manager,
            llm=self.llm,
        )

        # self.multi_party_agent = OpenAIAgent.from_tools(
        #     tools=all_tools,
        #     system_prompt=SYSTEM_PROMPT_MULTI_PARTY,
        #     llm=self.llm,
        #     verbose=True,
        #     callback_manager=callback_manager,
        # )
