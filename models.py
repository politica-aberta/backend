from llama_index import VectorStoreIndex
from llama_index.llms import ChatMessage
from llama_index.chat_engine import SimpleChatEngine
from llama_index.memory import ChatMemoryBuffer


parties = {
    "PS": "Partido Socialista",
    "PSD": "Partido Social Democrata",
    "CHEGA": "Partido Chega",
    "PAN": "Pessoas - Animais - Natureza",
    "LIVRE": "Partido Livre",
    "BE": "Bloco de Esquerda",
    "IL": "Iniciativa Liberal",
    "PCP": "Partido Comunista Português"
}


class PoliticalParty:
    def __init__(self, party_name, index):
        self.name = party_name
        self.full_name = parties[party_name]
        self.index = index


class PoliticalPartyManager:
    def __init__(self):
        self.political_parties = {}

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


class Conversation:
    def __init__(
        self,
        chat_mode,
        political_party = None,
        similarity_top_k = None,
        system_prompt = None,
        node_postprocessors=None,
        service_context=None,
        previous_messages_token_limit=None
    ):
        if chat_mode == "context":
            self.chat_engine = political_party.index.as_chat_engine(
                chat_mode=chat_mode,
                similarity_top_k=similarity_top_k,
                system_prompt=system_prompt,
                node_postprocessors=node_postprocessors,
                memory=ChatMemoryBuffer.from_defaults(token_limit=previous_messages_token_limit)
            )
        elif chat_mode == "simple":
            self.chat_engine = SimpleChatEngine.from_defaults(system_prompt=system_prompt, service_context=service_context, memory=ChatMemoryBuffer.from_defaults(token_limit=previous_messages_token_limit))

    def chat(self, prompt, previous_messages):
        prefix_messages = [ChatMessage(role=message["role"], content=message["content"]) for message in previous_messages]

        return self.chat_engine.chat(prompt, chat_history=prefix_messages)
    
    def stream_chat(self, prompt, previous_messages):
        prefix_messages = [ChatMessage(role=message["role"], content=message["content"]) for message in previous_messages]

        return self.chat_engine.stream_chat(prompt, chat_history=prefix_messages)
