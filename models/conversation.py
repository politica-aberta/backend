from llama_index.llms import ChatMessage
from llama_index.chat_engine import SimpleChatEngine
from llama_index.memory import ChatMemoryBuffer

from .party import PoliticalParty

class Conversation:
    def __init__(
        self,
        chat_mode,
        political_party: PoliticalParty | None = None,
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
