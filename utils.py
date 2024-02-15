import os
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

from constants import DOCUMENT_DIR
from pathlib import Path

from typing import Dict, List, Optional


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




class MuPDFReader(BaseReader):
    """PDF parser using PyMuPDF library."""

    # def __init__(self, return_full_document: Optional[bool] = False) -> None:
    #     """
    #     Initialize PDFReader.
    #     """
    #     self.return_full_document = return_full_document

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[Document]:
        """Parse file."""
        try:
            import fitz
        except ImportError:
            raise ImportError(
                "PyMuPDF is required to read PDF files: `pip install PyMuPDF`"
            )
        
        docs = []
        doc = fitz.open(file)

        for page in doc:
            page_text = page.get_text(flags=fitz.TEXTFLAGS_SEARCH)
            page_number = page.number+1

            metadata = {}

            metadata = {"page_number": page_number, "file_path": str(file)}
            if extra_info is not None:
                metadata.update(extra_info)

            docs.append(Document(text=page_text, metadata=metadata))
        return docs