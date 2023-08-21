from llama_index import ServiceContext
from llama_index.llms import OpenAI
from  llama_index.embeddings.openai import OpenAIEmbedding
from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from models import *
import weaviate
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import StorageContext
from llama_index.indices.composability import ComposableGraph
from llama_index.indices.keyword_table import GPTKeywordTableIndex
import time
import requests

# Constants

document_dir = "docs/"
weviate_url = "http://weaviate:8080"
SIMILARITY_TOP_K = 5
SYSTEM_PROMPT = "Caro agente, a sua tarefa consiste em responder a perguntas sobre documentos políticos de partidos portugueses. \
    Quando receber uma pergunta, deve analisar os documentos relevantes e fornecer uma resposta que espelhe o conteúdo dos documentos, sem acrescentar a sua própria opinião ou interpretação. \
    A sua resposta deve ser objectiva e imparcial, centrando-se exclusivamente na informação presente nos documentos. Se a informação não estiver nos documentos, indique isso na sua resposta. \
    Exemplo de pergunta: Qual é a posição do Partido X acerca do tema Y? \
    Resposta adequada: De acordo com o documento Z do Partido X, a posição do partido acerca do tema Y é [...]. \
    Resposta inadequada: Acredito que a posição do Partido X acerca do tema Y é [...]. \
    Recorde-se de que a sua função é facilitar o acesso à informação contida nos documentos políticos, sem expressar opiniões pessoais ou interpretações."

embed_model = OpenAIEmbedding(embed_batch_size=500)
llm = OpenAI(model="gpt-3.5-turbo-16k")
service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

# Global Variables

active_conversations = {}
all_political_parties = {}
graph = {} # TODO Dirty Fix

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

    db_client.schema.delete_all()

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

        vector_store = WeaviateVectorStore(weaviate_client=db_client, index_name=party.upper())
        summary = f'Programa eleitoral do {val.value} ({party}) para as legislativas de 2022.' # TODO Dirty Fix, only works for one document
        all_political_parties[val] = PoliticalParty(val, summary, docs_to_index(docs, StorageContext.from_defaults(vector_store=vector_store)))


def create_composable_graph():
    db_client = weaviate.Client(weviate_url)

    values = all_political_parties.values()

    indexes = list(map(lambda x: x.index, values))
    index_summaries = list(map(lambda x: x.summary, values))

    vector_store = WeaviateVectorStore(weaviate_client=db_client, index_name="ComposableGraph") # TODO Hardcoded
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    graph["ComposableGraph"] = ComposableGraph.from_indices(                # TODO Dirty Fix
        GPTKeywordTableIndex,
        children_indices=indexes,
        index_summaries=index_summaries,
        service_context=service_context,
        storage_context=storage_context
    ).as_query_engine(system_prompt=SYSTEM_PROMPT)

def process_query_composable_graph(query):

    raw_answer = graph["ComposableGraph"].query(query)

    reply = raw_answer.response

    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))

    return coordinates, reply


def process_chat(id, political_party_name, query_text):
    if id not in active_conversations:
        active_conversations[id] = Conversation(id, all_political_parties[political_party_name], SIMILARITY_TOP_K, SYSTEM_PROMPT)
    
    raw_answer = active_conversations[id].chat(query_text)    
    
    reply = raw_answer.response

    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))

    return coordinates, reply


def finish_conversation(conversation_id):
    if conversation_id not in active_conversations:
        return f'Conversation with {conversation_id} not found.'

    del active_conversations[conversation_id]
