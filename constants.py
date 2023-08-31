from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from models import *

# Server Constants

WEAVIATE_PORT = "8080"
SUPABASE_URL = "https://dzwdgfmvuevjqjutrpye.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6d2RnZm12dWV2anFqdXRycHllIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI5NTcwMTgsImV4cCI6MjAwODUzMzAxOH0.oWDnME53bTI43Y2eHhe1clNgOVV6dcya6-x3ZIGLT9k"

# Supabase Constants

SUPABASE_USER_TABLE = "user_data"
SUPABASE_CONVERSATION_TABLE = "conversation_data"
SUPABASE_POLITICAL_PARTY_TABLE = "political_party_data"

# Base Models

EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500)
LLM = OpenAI(model="gpt-3.5-turbo")

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

# Usage Constants

MAX_USAGE = 1

# Global Variables

conversation_manager = ConversationManager()
political_party_manager = PoliticalPartyManager()
graph = {}  # TODO Dirty Fix
