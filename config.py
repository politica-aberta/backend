from llama_index.vector_stores import SupabaseVectorStore
from llama_index import VectorStoreIndex, SummaryIndex

from constants import SUPABASE_POSTGRES_CONNECTION_STRING
from models import parties
from models.party import PoliticalParty
from globals import political_party_manager, service_context
from llama_index.readers import PDFReader


def initialize_indexes():
    
    loader = PDFReader()

    for name, fullname in parties.items():
        
        print("initializing " + name + "....")

        vector_store = SupabaseVectorStore(
            postgres_connection_string=SUPABASE_POSTGRES_CONNECTION_STRING,
            collection_name=name,
        )

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

        party = PoliticalParty(name, index)
        
        party.import_party_files(reader=loader)
        
        # party.generate_summary_index() # TODO: is this neceessary?
        
        party.set_agent()

        political_party_manager.insert(party)
        
    print("initializing multi party agent...")
    political_party_manager.generate_multi_party_agent()
    
if __name__ == "__main__":
    initialize_indexes()