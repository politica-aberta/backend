import os

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index.core.service_context import ServiceContext

from models.manager import PoliticalPartyManager

# Base Models

print(
    "initializing models with the following openai_key",
    os.environ.get("OPENAI_API_KEY"),
)
EMBED_MODEL = OpenAIEmbedding(
    embed_batch_size=500, model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE
)
LLM = OpenAI(model="gpt-3.5-turbo-0125")

political_party_manager = PoliticalPartyManager(llm=LLM)
service_context = ServiceContext.from_defaults(
    llm=LLM,
    embed_model=EMBED_MODEL,
)
