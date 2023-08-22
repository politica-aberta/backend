from enum import Enum
from llama_index import VectorStoreIndex
from llama_index.vector_stores import WeaviateVectorStore

import os


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

    def document_path(self):
        # FIXME assuming 1 doc per party, to add more just create a folder per party
        filename = f"{self.name.lower()}-legislativas22.pdf"
        return os.path.join("/docs", filename)


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
