from llama_index.chat_engine.types import ChatMode
from llama_index.llms import ChatMessage
import logging
import fitz
import requests
from models.conversation import Conversation
from llama_index import ServiceContext
from llama_index.postprocessor.cohere_rerank import CohereRerank

from globals import political_party_manager, service_context
from constants import (
    SIMILARITY_TOP_K,
    TOKEN_LIMIT,
    system_prompt_specific_party,
)
from llama_index.prompts import PromptTemplate


from postprocessor import ExcludeMetadataKeysNodePostprocessor


def get_references(raw_answer, party_name=None):
    def convert_file_format(path):
        """some docs have a file format of 'docs/{party}/legislativas22.pdf}
        while the supposed format is {party.lower()}/legislativas22.pdf}"""
        supabase_prefix = "https://dzwdgfmvuevjqjutrpye.supabase.co/storage/v1/object/public/documents/"
        tokens = path.split("/")
        path = f"{tokens[1].lower()}-{tokens[2]}" if len(tokens) == 3 else path
        return supabase_prefix + path, tokens[1]

    parties: dict[str, list[str, dict[int, list[str]]]] = {}

    for node in raw_answer.source_nodes:
        if "file_path" in node.metadata:
            document, party = convert_file_format(node.metadata["file_path"])
            if party not in parties:
                parties[party] = [document, {}]

            if "page_number" in node.metadata:
                page_number = int(node.metadata["page_number"])
                if page_number in parties[party][1]:
                    parties[party][1][page_number].append(node.text)
                else:
                    parties[party][1][page_number] = [node.text]
    # TODO: sort by doc as well (?)
    references = [
        {
            "party": party_name if party_name else party,
            "document": pages[0],
            "pages": pages[1],
        }
        for party, pages in parties.items()
    ]

    return references

# TODO: Can be optimized
def get_highlight_boxes(references):
    for ref in references:
        response = requests.get(ref["document"])
        response.raise_for_status() 

        doc = fitz.open(stream=response.content, filetype="pdf")
        for page, text_excerpts in ref["pages"].items():
            highlight_boxes = []
            for text in text_excerpts:
                highlight_boxes.extend([
                    [rect.x0, rect.y0, rect.x1, rect.y1]
                    for rect in  doc[page-1].search_for(text)])
            ref["pages"][page] = highlight_boxes

async def process_multi_party_chat(
    parties, chat_text, previous_messages, infer_chat_mode_flag, stream=False
):
    if not political_party_manager.multi_party_agent:
        raise Exception("No multi-party agent found.")

    out = query_rewrite(chat_text, previous_messages, service_context)

    prefix_messages = [
        ChatMessage(role=message.role, content=message.message)
        for message in previous_messages
    ]

    response = await political_party_manager.multi_party_agent.achat(out, prefix_messages)

    references = get_references(response)
    return response.response, references


def process_chat(
    party_name, chat_text, previous_messages, infer_chat_mode_flag, stream=False
):
    party = political_party_manager.get(party_name)

    out = query_rewrite(chat_text, previous_messages, service_context)

    conversation = Conversation(
        (
            infer_chat_mode(chat_text, previous_messages, service_context)
            if infer_chat_mode_flag
            else ChatMode.CONTEXT
        ),
        party=party,
        similarity_top_k=SIMILARITY_TOP_K,
        system_prompt=system_prompt_specific_party(
            full_name=party.full_name, name=party.name
        ),
        node_postprocessors=[
            ExcludeMetadataKeysNodePostprocessor(),
            CohereRerank(
                model="rerank-multilingual-v2.0",
                top_n=4,
            ),
        ],
        previous_messages_token_limit=TOKEN_LIMIT,
        service_context=service_context,
    )

    if stream:
        raw_answer = conversation.stream_chat(chat_text, previous_messages)
        answer = raw_answer.response_gen

    else:
        raw_answer = conversation.chat(out, previous_messages)
        answer = raw_answer.response

    references = get_references(raw_answer=raw_answer, party_name=party_name)

    get_highlight_boxes(references)

    return answer, references


def infer_chat_mode(chat_text, previous_messages, service_context: ServiceContext):

    # FIXME use previous_messages

    query_gen_str = """
    Para determinar o modo de resposta mais adequado, responde apenas com "simple" ou "context". 
    Se a mensagem está diretamente relacionada com informações contidas nos documentos sobre partidos políticos, responda com "context". 
    Se a mensagem aparenta estar relacionada apenas com a conversa em si e não requer informações dos documentos políticos, responda com "simple". 
    Se nenhuma das opções acima se aplicar claramente, opte por responder com "context" para minimizar falsos positivos.
    A mensagem é a seguinte:
    
    {chat_text}

    Modo de resposta:
    """

    query_gen_prompt = PromptTemplate(query_gen_str)

    chat_mode = service_context.llm.predict(
        query_gen_prompt, previous_messages=previous_messages, chat_text=chat_text
    )

    return (
        chat_mode
        if chat_mode in (ChatMode.SIMPLE, ChatMode.CONTEXT)
        else ChatMode.CONTEXT
    )


def query_rewrite(query: str, previous_messages: list, service_context: ServiceContext):

    query_gen_str = """
    És um assistente cujo trabalho é reescrever a pergunta do utilizador para que seja mais fácil de pesquisar no nosso sistema, deves usar maioritariamente keywords e remover palavras de ligação.
    Deves ter em atenção ao histórico de mensagens abaixo:

    {previous_messages}

    Se o utilizador fizer uma referência ao histórico (por exemplo: "repete o ponto x", "clarifica o último tópico"), repete o respetivo contexto relevante na nova pergunta.
    Especifica qual o partido em questao na nova pergunta.
    Pergunta do utilizador:

    {query}

    Nova pergunta:
    """

    query_gen_prompt = PromptTemplate(query_gen_str)

    rewritten_q = service_context.llm.predict(
        query_gen_prompt, previous_messages=previous_messages, query=query
    )
    logging.info(f"Rewritten query: {rewritten_q}")

    return rewritten_q
