from llama_index import StorageContext
from llama_index.vector_stores import SupabaseVectorStore

from constants import *
from models import *
from utils import *

def populate_vector_database():

    for name, _ in parties.items():

        vector_store = SupabaseVectorStore(
        postgres_connection_string=SUPABASE_POSTGRES_CONNECTION_STRING,
        collection_name=name,
        )

        docs = load_documents([get_document_path(name, doc) for doc in DOCUMENTS])

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        _ = docs_to_index(docs, storage_context)

if __name__ == "__main__":
    populate_vector_database()