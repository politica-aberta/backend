from models import *
from constants import *
from utils import *

def start_conversation(user_id, political_party, supabase):
    conversation = supabase.table(SUPABASE_CONVERSATION_TABLE).insert({"user_id": user_id, "entity": political_party}).execute()
    
    id = get_conversation_id(conversation)

    party = political_party_manager.get(political_party)
    
    conversation_manager.insert(Conversation(id, party, SIMILARITY_TOP_K, SYSTEM_PROMPT))
    
    return id

def process_chat(id, query_text):
    conversation = conversation_manager.get(id)

    raw_answer = conversation.chat(query_text)
    
    reply = raw_answer.response
    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))
    
    return coordinates, reply


def process_query_composable_graph(query):
    raw_answer = graph["ComposableGraph"].query(query)

    reply = raw_answer.response

    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))

    return coordinates, reply


def finish_conversation(conversation_id):
    conversation_manager.delete(conversation_id)

    return f"Successful deletion of conversation with id {conversation_id}"
