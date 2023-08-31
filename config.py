import requests
import time

from llama_index.vector_stores import WeaviateVectorStore
from llama_index import StorageContext
from llama_index.indices.composability import ComposableGraph
from llama_index.indices.keyword_table import GPTKeywordTableIndex

from constants import *
from models import *
from utils import *


def wait_for_weaviate():
    while True:
        try:
            response = requests.get(f'http://weaviate:{WEAVIATE_PORT}/v1/.well-known/live')
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(5)


def initialize_indexes():
    db_client = get_weaviate_client()

    for name, fullname in parties.items():
        vector_store = WeaviateVectorStore(
            weaviate_client=db_client, index_name=name
        )

        party = PoliticalParty(name, fullname)

        docs = load_documents([get_document_path(party.name, doc) for doc in DOCUMENTS])

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        party.index = docs_to_index(docs, storage_context)

        political_party_manager.insert(party)


def create_composable_graph():
    db_client = get_weaviate_client()

    values = political_party_manager.get_all()

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
        service_context=get_service_context(),
        storage_context=storage_context,
    ).as_query_engine(system_prompt=SYSTEM_PROMPT)