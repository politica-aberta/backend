import weaviate
import redis
import os
from llama_index import SimpleDirectoryReader
from llama_index import ServiceContext
from constants import *
from llama_index import VectorStoreIndex

def load_documents(documents):
    reader = SimpleDirectoryReader(input_files=documents)
    parsed_doc = reader.load_data()

    return parsed_doc

def get_weaviate_client():
    return weaviate.Client(f"http://weaviate:{WEAVIATE_PORT}")

def get_redis_client():
    return redis.Redis(host="redis", port=REDIS_PORT, db=REDIS_DB)

def get_service_context():
    return ServiceContext.from_defaults(llm=LLM, embed_model=EMBED_MODEL)

def clean_weviate_database():
    db_client = get_weaviate_client()
    db_client.schema.delete_all()

def docs_to_index(docs, storage_context):
    return VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,  # TODO Dirty Fix, only works for one document (should be fixed now, remove after it runs successfully)
        service_context=get_service_context(),
    )

def get_document_path(party_name, document):
    return os.path.join(DOCUMENT_DIR, f"{party_name.lower()}-{document}.pdf")


def get_user_id(user):
    return user.user.id

def get_usage(raw_usage):
    return raw_usage.data[0]["usage"]