from llama_index.llms import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index import ServiceContext
from models import *

# Server Constants

SUPABASE_URL = "https://dzwdgfmvuevjqjutrpye.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6d2RnZm12dWV2anFqdXRycHllIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTI5NTcwMTgsImV4cCI6MjAwODUzMzAxOH0.oWDnME53bTI43Y2eHhe1clNgOVV6dcya6-x3ZIGLT9k"

# Supabase Constants

SUPABASE_USER_TABLE = "user_data"
SUPABASE_CONVERSATION_TABLE = "conversation_data"
SUPABASE_POLITICAL_PARTY_TABLE = "political_party_data"
SUPABASE_POSTGRES_USER = "postgres"
SUPABASE_POSTGRES_PASSWORD = "W9vo3k*BbfJj"
SUPABASE_POSTGRES_HOST = "db.dzwdgfmvuevjqjutrpye.supabase.co"
SUPABASE_POSTGRES_PORT = "5432"
SUPABASE_POSTGRES_DB_NAME = "postgres"
SUPABASE_POSTGRES_CONNECTION_STRING = f"postgresql://{SUPABASE_POSTGRES_USER}:{SUPABASE_POSTGRES_PASSWORD}@{SUPABASE_POSTGRES_HOST}:{SUPABASE_POSTGRES_PORT}/{SUPABASE_POSTGRES_DB_NAME}"

# Base Models

EMBED_MODEL = OpenAIEmbedding(embed_batch_size=500)
LLM = OpenAI(model="gpt-3.5-turbo")

# Prompt Related Constants

SIMILARITY_TOP_K = 5
SYSTEM_PROMPT = "Caro agente, a sua tarefa consiste em responder a perguntas sobre documentos políticos de partidos portugueses. \
    Quando receber uma pergunta, deve analisar os documentos relevantes e fornecer uma resposta que espelhe o conteúdo dos documentos, sem acrescentar a sua própria opinião ou interpretação. \
    A sua resposta deve ser objectiva e imparcial, centrando-se exclusivamente na informação presente nos documentos. Se a informação não estiver nos documentos, indique isso na sua resposta. \
    Exemplo de pergunta: Qual é a posição do Partido X acerca do tema Y? \
    Resposta adequada: De acordo com o documento Z do Partido X, a posição do partido acerca do tema Y é ... [45], assim como ... [93]. (onde 45 e 93 são as páginas usadas para redigir a resposta)\
    Resposta inadequada: Acredito que a posição do Partido X acerca do tema Y é [...]. \
    Recorde-se de que a sua função é facilitar o acesso à informação contida nos documentos políticos, sem expressar opiniões pessoais ou interpretações.\
    Se no contexto enviado não se encontrar a informação necessária para a resposta, indica que não conseguiste encontrar essa informação no documento"

DECISION_TEMPLATE = "Para determinar o modo de resposta mais adequado, responde apenas com \"simple\" ou \"context\". \n \
    Se a mensagem está diretamente relacionada com informações contidas nos documentos sobre partidos políticos, responda com \"context\". \n \
    Se a mensagem aparenta estar relacionada apenas com a conversa em si e não requer informações dos documentos políticos, responda com \"simple\". \n \
    Se nenhuma das opções acima se aplicar claramente, opte por responder com \"context\" para minimizar falsos positivos. \n \
    A mensagem é a seguinte: \n \
    {message}"
TOKEN_LIMIT = 1000

# Document Data

DOCUMENT_DIR = "docs/"
DOCUMENTS = ["legislativas22"] 

# Global Variables

political_party_manager = PoliticalPartyManager()
service_context = ServiceContext.from_defaults(llm=LLM, embed_model=EMBED_MODEL)
