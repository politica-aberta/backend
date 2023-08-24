from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from models import *

# Server Constants

WEAVIATE_PORT = "8080"
REDIS_PORT = "6379"
REDIS_DB = "0"

# Base Models

EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500)
LLM = OpenAI(model="gpt-3.5-turbo-16k")

# Prompt Related Constants

SIMILARITY_TOP_K = 5
SYSTEM_PROMPT = "Caro agente, a sua tarefa consiste em responder a perguntas sobre documentos políticos de partidos portugueses. \
    Quando receber uma pergunta, deve analisar os documentos relevantes e fornecer uma resposta que espelhe o conteúdo dos documentos, sem acrescentar a sua própria opinião ou interpretação. \
    A sua resposta deve ser objectiva e imparcial, centrando-se exclusivamente na informação presente nos documentos. Se a informação não estiver nos documentos, indique isso na sua resposta. \
    Exemplo de pergunta: Qual é a posição do Partido X acerca do tema Y? \
    Resposta adequada: De acordo com o documento Z do Partido X, a posição do partido acerca do tema Y é [...]. \
    Resposta inadequada: Acredito que a posição do Partido X acerca do tema Y é [...]. \
    Recorde-se de que a sua função é facilitar o acesso à informação contida nos documentos políticos, sem expressar opiniões pessoais ou interpretações."

# Document Data


DOCUMENT_DIR = "docs/"
DOCUMENTS = ["legislativas22"] 

# Global Variables

conversation_manager = ConversationManager()
political_party_manager = PoliticalPartyManager()
graph = {}  # TODO Dirty Fix
