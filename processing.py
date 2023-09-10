from models import *
from constants import *
from utils import *

def process_chat(political_party, chat_text, previous_messages):
    party = political_party_manager.get(political_party)

    conversation = Conversation(party, SIMILARITY_TOP_K, SYSTEM_PROMPT)

    raw_answer = conversation.chat(chat_text, previous_messages)
    
    reply = raw_answer.response
    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))
    
    return coordinates, reply