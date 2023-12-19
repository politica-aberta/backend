from llama_index.postprocessor.types import BaseNodePostprocessor  

class ExcludeMetadataKeysNodePostprocessor(BaseNodePostprocessor):
    def postprocess_nodes(
        self,
        nodes,
        query_bundle = None,
    ):
        for node in nodes:
            node.node.excluded_llm_metadata_keys = ["file_name"]

        return nodes