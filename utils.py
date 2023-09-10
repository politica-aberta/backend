import os
from llama_index import SimpleDirectoryReader
from llama_index import ServiceContext
from constants import *
from llama_index import VectorStoreIndex

def load_documents(documents):
    reader = SimpleDirectoryReader(input_files=documents)
    parsed_doc = reader.load_data()

    return parsed_doc

def get_service_context():
    return ServiceContext.from_defaults(llm=LLM, embed_model=EMBED_MODEL)

def docs_to_index(docs, storage_context):
    return VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        service_context=get_service_context(),
    )

def get_document_path(party_name, document):
    return os.path.join(DOCUMENT_DIR, f"{party_name.lower()}-{document}.pdf")

def get_user_id(user):
    return user.user.id

def get_conversation_id(raw_conversation):
    return raw_conversation.data[0]["id"]