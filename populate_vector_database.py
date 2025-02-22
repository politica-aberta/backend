import os
from llama_index.core import StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore



# from constants import SUPABASE_POSTGRES_CONNECTION_STRING
from utils import MuPDFReader
from models import parties
from models.party import PoliticalParty


class DataLoader:
    loader = MuPDFReader()
    
    def __init__(self):
        self.all_docs = []
        self.parties: list[PoliticalParty] = []
        for key in parties.keys():
            self.parties.append(PoliticalParty(party_name=key, index = None))
    
    
    def populate_vector_database(self):

        for party in self.parties:
                        
            print(party.name)
            print("Importing files...")
            party.import_party_files(reader=self.loader)
            print("Imported!")

            # docs = load_documents([get_document_path(name, doc) for doc in DOCUMENTS], f"Programa eleitoral do {name} para as eleições legislativas de 2022.")
            # vector_store = SupabaseVectorStore(
            #     postgres_connection_string=SUPABASE_POSTGRES_CONNECTION_STRING,
            #     collection_name=party.name,
            # )
            vector_store = MilvusVectorStore(
                collection_name=party.name,
                dim=3072,
                uri=os.environ["MILVUS_URI"],
                overwrite=True
            )
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            print("generating indices for party")
            party.generate_index(storage_context=storage_context)
            

if __name__ == "__main__":
    data_loader = DataLoader()
    data_loader.populate_vector_database()