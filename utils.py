from llama_index import SimpleDirectoryReader


def load_document(document_name):
    reader = SimpleDirectoryReader(input_files=[document_name])
    parsed_doc = reader.load_data()

    return parsed_doc
