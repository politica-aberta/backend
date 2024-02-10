import os

from llama_index.llms import OpenAI, MistralAI
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index import ServiceContext

from models.manager import PoliticalPartyManager

# Base Models

print(
    "initializing models with the following openai_key",
    os.environ.get("OPENAI_API_KEY"),
)
EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500, model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE)
LLM = OpenAI(model="gpt-3.5-turbo-1106")
# LLM = MistralAI(model="mistral-small")


political_party_manager = PoliticalPartyManager(llm=LLM)
service_context = ServiceContext.from_defaults(
    llm=LLM,
    embed_model=EMBED_MODEL,
)
