from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index import ServiceContext

from models.manager import PoliticalPartyManager

# Base Models

EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500)
LLM = OpenAI(model="gpt-3.5-turbo-1106")


political_party_manager = PoliticalPartyManager()
service_context = ServiceContext.from_defaults(llm=LLM, embed_model=EMBED_MODEL)