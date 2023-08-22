import weaviate
import redis

from llama_index import ServiceContext
from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index import VectorStoreIndex

from llama_index.vector_stores import WeaviateVectorStore
from llama_index import StorageContext
from llama_index.indices.composability import ComposableGraph
from llama_index.indices.keyword_table import GPTKeywordTableIndex

from models import *
from utils import load_document

# Constants

document_dir = "docs/"
weaviate_url = "http://weaviate:8080"
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

weaviate_client = weaviate.Client(weaviate_url)
redis_client = redis.Redis(host="localhost", port=6379, db=0)


# Global Variables

active_conversations = {}
all_political_parties = {}
graph = {}  # TODO Dirty Fix


def clean_database():
    db_client = weaviate.Client(weaviate_url)
    db_client.schema.delete_all()


def docs_to_index(docs, storage_context):
    return VectorStoreIndex.from_documents(
        docs["legislativas22"],
        storage_context=storage_context,  # TODO Dirty Fix, only works for one document
        service_context=service_context,
    )


def initialize_indexes():
    for name, fullname in parties.items():
        vector_store = WeaviateVectorStore(
            weaviate_client=weaviate_client, index_name=name
        )

        party = PoliticalParty(name, fullname)
        # FIXME switch this to a dir per party in the future
        docs = dict(
            (doc, load_document(party.document_path())) for doc in ["legislativas22"]
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        party.index = docs_to_index(docs, storage_context)

        all_political_parties[name] = party


def initialize_redis():
    # TODO move active conversations to redis
    redis_client.set("chat_counter", 0)


def create_composable_graph():
    db_client = weaviate.Client(weaviate_url)

    values = all_political_parties.values()

    indexes = list(map(lambda x: x.index, values))
    index_summaries = list(map(lambda x: x.summary, values))

    vector_store = WeaviateVectorStore(
        weaviate_client=db_client, index_name="ComposableGraph"
    )  # TODO Hardcoded
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    graph["ComposableGraph"] = ComposableGraph.from_indices(  # TODO Dirty Fix
        GPTKeywordTableIndex,
        children_indices=indexes,
        index_summaries=index_summaries,
        service_context=service_context,
        storage_context=storage_context,
    ).as_query_engine(system_prompt=SYSTEM_PROMPT)


def process_query_composable_graph(query):
    raw_answer = graph["ComposableGraph"].query(query)

    reply = raw_answer.response

    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))

    return coordinates, reply


def process_chat(id, query_text):
    if id not in active_conversations:
        raise ValueError("Conversation ID not found")

    raw_answer = active_conversations[id].chat(query_text)
    reply = raw_answer.response
    coordinates = list(map(lambda x: x.node.metadata, raw_answer.source_nodes))
    return coordinates, reply


def start_conversation(political_party):
    party = all_political_parties[political_party]
    active_conversations[id] = Conversation(id, party, SIMILARITY_TOP_K, SYSTEM_PROMPT)
    id = redis_client.incr(name="chat_counter")
    return id


def finish_conversation(conversation_id):
    if conversation_id not in active_conversations:
        return f"Conversation with {conversation_id} not found."

    del active_conversations[conversation_id]
