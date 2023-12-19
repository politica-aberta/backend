
from llama_index import QueryBundle
from llama_index.postprocessor.types import BaseNodePostprocessor
from llama_index.schema import NodeWithScore
from typing import List, Optional


class ExcludeMetadataKeysNodePostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle]
    ) -> List[NodeWithScore]:
        # subtracts 1 from the score
        for node in nodes:
            node.node.excluded_llm_metadata_keys = ["file_name"]

        return nodes