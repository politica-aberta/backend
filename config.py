import os

from llama_index.vector_stores import MilvusVectorStore
from llama_index import VectorStoreIndex, SummaryIndex

from models import parties
from models.party import PoliticalParty
from globals import political_party_manager, service_context
# from llama_index.readers import PDFReader


def initialize_indexes():
    
    # loader = PDFReader()

    for name, fullname in parties.items():
        
        print("initializing " + name + "....")

        vector_store = MilvusVectorStore(
            collection_name=name,
            uri=os.environ["MILVUS_URI"]
        )

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

        party = PoliticalParty(name, index)
        
        # party.import_party_files(reader=loader)
        
        # party.generate_summary_index() # TODO: is this neceessary?
        
        party.set_agent()

        political_party_manager.insert(party)
        
    print("initializing multi party agent...")
    political_party_manager.generate_multi_party_agent()
    
if __name__ == "__main__":
    initialize_indexes()