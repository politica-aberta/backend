from llama_index import ServiceContext
from llama_index.llms import OpenAI
from  llama_index.embeddings.openai import OpenAIEmbedding
from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from models import *
import weaviate
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import StorageContext
import time
import requests

# Constants

document_dir = "docs/"
embed_model = OpenAIEmbedding(embed_batch_size=500)
llm = OpenAI(model="gpt-3.5-turbo-16k")
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
weviate_url = "http://weaviate:8080"

# Global Variables

active_conversations = {}
all_political_parties = {}

def wait_for_weaviate():
    while True:
        try:
            response = requests.get('http://weaviate:8080/v1/.well-known/live')
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(5)

def clean_database():
    db_client = weaviate.Client(weviate_url)

    for val in PoliticalPartyName:
        party = str(val).split(".")[1]

        db_client.schema.delete_class(party)

def load_document(document_name):
    reader = SimpleDirectoryReader(input_files=[document_name])
    parsed_doc = reader.load_data()

    return parsed_doc

def docs_to_index(docs, storage_context):
    return VectorStoreIndex.from_documents(
        docs["legislativas22"], storage_context=storage_context, # TODO Dirty Fix, only works for one document
        service_context=service_context
        )

def initialize_indexes():
    db_client = weaviate.Client(weviate_url)

    for val in PoliticalPartyName:
        party = str(val).split(".")[1].lower()
        docs = {}
        for document in ["legislativas22"]:
            docs[document] = load_document(document_dir + party + "-" + document + ".pdf")

        vector_store = WeaviateVectorStore(weaviate_client=db_client, index_name= party.upper())
        all_political_parties[val] = PoliticalParty(val, docs_to_index(docs, StorageContext.from_defaults(vector_store=vector_store)))


def process_query(id, political_party_name, query_text):
    if id not in active_conversations:
        active_conversations[id] = Conversation(id, all_political_parties[political_party_name])
    
    answer = active_conversations[id].chat(query_text)    
    
    # Dummy response for demonstration purposes
    coordinates = {'x': 123, 'y': 456}

    return coordinates, answer


def finish_conversation(conversation_id):
    if conversation_id not in active_conversations:
        return f'Conversation with {conversation_id} not found.'

    del active_conversations[conversation_id]
