import os
from llama_index import SimpleDirectoryReader, Document
from llama_index.readers.base import BaseReader
from llama_index.readers import PDFReader
from llama_index import VectorStoreIndex

from globals import service_context
from constants import DOCUMENT_DIR


def load_documents(documents, description):
    reader = SimpleDirectoryReader(input_files=documents)
    parsed_doc = reader.load_data(extra_info={})

    return parsed_doc



def get_document_path(party_name, document):
    return os.path.join(DOCUMENT_DIR, f"{party_name.lower()}-{document}.pdf")

def get_user_id(user):
    return user.user.id

def get_conversation_id(raw_conversation):
    return raw_conversation.data[0]["id"]
