from llama_index.vector_stores import SupabaseVectorStore
from llama_index import VectorStoreIndex

from constants import SUPABASE_POSTGRES_CONNECTION_STRING, service_context
from models import  PoliticalParty, parties
from utils import political_party_manager

def initialize_indexes():

    for name, fullname in parties.items():

        vector_store = SupabaseVectorStore(
        postgres_connection_string=SUPABASE_POSTGRES_CONNECTION_STRING,
        collection_name=name,
        )

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

        party = PoliticalParty(name, index)

        political_party_manager.insert(party)