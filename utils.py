import os
from llama_index import SimpleDirectoryReader
from constants import *
from llama_index import VectorStoreIndex

def load_documents(documents, description):
    reader = SimpleDirectoryReader(input_files=documents, extra_info={"description": description})
    parsed_doc = reader.load_data()

    return parsed_doc

def docs_to_index(docs, storage_context):
    return VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        service_context=service_context,
    )

def get_document_path(party_name, document):
    return os.path.join(DOCUMENT_DIR, f"{party_name.lower()}-{document}.pdf")

def get_user_id(user):
    return user.user.id

def get_conversation_id(raw_conversation):
    return raw_conversation.data[0]["id"]
