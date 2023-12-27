from llama_index.chat_engine.types import ChatMode

from models.conversation import Conversation
from globals import political_party_manager, service_context
from constants import SIMILARITY_TOP_K, SYSTEM_PROMPT, TOKEN_LIMIT, DECISION_TEMPLATE
from postprocessor import ExcludeMetadataKeysNodePostprocessor

def process_chat(political_party, chat_text, previous_messages, infer_chat_mode_flag, stream=False):
    party = political_party_manager.get(political_party)
    # TODO: Should we use ChatMode.BEST??
    if infer_chat_mode_flag:
        conversation = Conversation(infer_chat_mode(chat_text, previous_messages), political_party=party, similarity_top_k=SIMILARITY_TOP_K, system_prompt=SYSTEM_PROMPT, node_postprocessors=[ExcludeMetadataKeysNodePostprocessor()], previous_messages_token_limit=TOKEN_LIMIT, service_context=service_context)

    else:
        conversation = Conversation(ChatMode.CONTEXT, political_party=party, similarity_top_k=SIMILARITY_TOP_K, system_prompt=SYSTEM_PROMPT, node_postprocessors=[ExcludeMetadataKeysNodePostprocessor()], previous_messages_token_limit=TOKEN_LIMIT)

    if stream:
        raw_answer = conversation.stream_chat(chat_text, previous_messages)
        reply = raw_answer.response_gen

    else:
        raw_answer = conversation.chat(chat_text, previous_messages)
        reply = raw_answer.response
    
    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))
    
    return coordinates, reply


def infer_chat_mode(chat_text, previous_messages):
    conversation = Conversation(ChatMode.SIMPLE, previous_messages_token_limit=TOKEN_LIMIT, service_context=service_context)

    raw_answer = conversation.chat(DECISION_TEMPLATE.format(message=chat_text), []) # CAN BE CHANGED TO IMPROVE PERFORMANCE
    
    chat_mode = raw_answer.response

    if chat_mode in (ChatMode.SIMPLE, ChatMode.CONTEXT):
        return chat_mode

    raise ValueError(f"Mode {chat_mode} does not exist")
