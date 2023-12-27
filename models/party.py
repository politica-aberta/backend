from pathlib import Path
from llama_index import VectorStoreIndex, StorageContext
from llama_index.readers.base import BaseReader
from llama_index.schema import Document

from . import parties
from globals import service_context
from constants import DOCUMENTS


class PoliticalParty:
    def __init__(self, party_name: str, index):
        self.name = party_name
        self.full_name = parties[party_name]
        self.index = index
        self.docs: list[Document] = []
    
    @staticmethod
    def docs_to_index(docs, storage_context: StorageContext):
        return VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            service_context=service_context,
            show_progress=True
        )
        
    def generate_index(self, storage_context: StorageContext):
        index = self.docs_to_index(
            docs = self.docs,
            storage_context=storage_context
        )
        self.index = index
        
    def import_party_files(self, reader: BaseReader):
        self.docs = []
        for doc in DOCUMENTS:
            out = reader.load_data(
                    file=Path(f"./docs/{self.name}/{doc}.pdf"),
                    extra_info={"description": f"Programa eleitoral do {self.full_name} para as eleições legislativas de 2022."}
                )
            self.docs.extend(out)
        # for d in self.docs:
        #     d.metadata = {"year": 2022} # TODO do not hardcode year