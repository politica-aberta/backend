import os

from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index import ServiceContext

from models.manager import PoliticalPartyManager

from constants import SYSTEM_PROMPT_MULTI_PARTY

# Base Models

print("initializing models with the following openai_key", os.environ.get("OPENAI_API_KEY"))
EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500)
LLM = OpenAI(model="gpt-3.5-turbo-1106")


political_party_manager = PoliticalPartyManager(llm=LLM)
service_context = ServiceContext.from_defaults(llm=LLM, embed_model=EMBED_MODEL, system_prompt=SYSTEM_PROMPT_MULTI_PARTY)