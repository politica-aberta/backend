from llama_index import VectorStoreIndex


parties = {
    "PS": "Partido Socialista",
    "PSD": "Partido Social Democrata"
    # "CHEGA": "Partido Chega",
    # "PAN": "Pessoas - Animais - Natureza",
    # "LIVRE": "Partido Livre",
    # "BE": "Bloco de Esquerda",
    # "IL": "Iniciativa Liberal",
    # "PCP": "Partido Comunista Português"
}


class PoliticalParty:
    name: str
    full_name: str
    summary: str
    index: VectorStoreIndex

    def __init__(self, party_name: str, party_full_name: str):
        self.name = party_name
        self.full_name = parties[party_name]
        self.summary = f"Programa eleitoral do {party_full_name} ({party_name}) para as legislativas de 2022."

    def __repr__(self):
        return f"PoliticalParty(name={self.name.value}, docs={list(self.index_store)})"


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
        conversation_id: int,
        political_party: PoliticalParty,
        similarity_top_k: int,
        system_prompt: str,
    ):
        self.conversation_id = conversation_id
        self.chat_engine = political_party.index.as_chat_engine(
            chat_mode="context",
            similarity_top_k=similarity_top_k,
            system_prompt=system_prompt,
        )

    def chat(self, prompt):
        return self.chat_engine.chat(prompt)

    def __repr__(self):
        return f"Conversation(id={self.conversation_id})"

    def __del__(self):
        self.chat_engine.reset()


class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def insert(self, conversation):
        id = conversation.conversation_id

        if id in self.conversations:
            raise ValueError("Conversation ID already exists")
        
        self.conversations[id] = conversation

    def get(self, conversation_id):
        if conversation_id not in self.conversations:
            raise ValueError("Conversation ID does not exist")
        return self.conversations[conversation_id]
    
    def delete(self, conversation_id):
        if conversation_id not in self.conversations:
            raise ValueError("Conversation ID does not exist")
        del self.conversations[conversation_id]

    def __del__(self):
        self.conversations.clear()
