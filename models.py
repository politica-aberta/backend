from enum import Enum

class PoliticalPartyName(Enum):
    PS = "Partido Socialista"
    PSD = "Partido Social Democrata"
    # CHEGA = "Partido Chega"
    # PAN = "Pessoas - Animais - Natureza"
    # LIVRE = "Partido Livre"
    # BE = "Bloco de Esquerda"
    # IL = "Iniciativa Liberal"
    # PCP = "Partido Comunista Português"

class PoliticalParty:
    
    def __init__(self, party_name: PoliticalPartyName, summary: str, party_index):
        self.name = party_name
        self.summary = summary
        self.index = party_index

    def __repr__(self):
        return f'PoliticalParty(name={self.name.value}, docs={list(self.index_store)})'


class Conversation:
    def __init__(self, conversation_id: int, political_party: PoliticalParty, similarity_top_k: int, system_prompt: str):
        self.conversation_id = conversation_id
        self.chat_engine = political_party.index.as_chat_engine(chat_mode="context", similarity_top_k=similarity_top_k, system_prompt=system_prompt)

    def chat(self, prompt):
        return self.chat_engine.chat(prompt)

    def __repr__(self):
        return f'Conversation(id={self.conversation_id})'

    def __del__(self):
        self.chat_engine.reset()
