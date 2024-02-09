from llama_index.chat_engine.types import ChatMode
from llama_index.llms import ChatMessage
import logging
from models.conversation import Conversation
from llama_index import ServiceContext
from globals import political_party_manager, service_context
from constants import (
    SIMILARITY_TOP_K,
    TOKEN_LIMIT,
    DECISION_TEMPLATE,
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

    parties: dict[str, list[str, set[int]]] = {}

    for node in raw_answer.source_nodes:
        if "file_name" in node.node.metadata:
            document, party = convert_file_format(node.node.metadata["file_name"])
            if party not in parties:
                parties[party] = [document, set()]

            if "page_label" in node.node.metadata:
                parties[party][1].add(int(node.node.metadata["page_label"]))

    references = [
        {
            "party": party_name if party_name else party,
            "document": pages[0],
            "pages": list(pages[1]),
        }
        for party, pages in parties.items()
    ]

    return references


def process_multi_party_chat(
    parties, chat_text, previous_messages, infer_chat_mode_flag, stream=False
):
    if not political_party_manager.multi_party_agent:
        raise Exception("No multi-party agent found.")
    prefix_messages = [
        ChatMessage(role=message["role"], content=message["message"])
        for message in previous_messages
    ]
    response = political_party_manager.multi_party_agent.chat(
        chat_text, prefix_messages
    )

    references = get_references(response)
    return response.response, references


def process_chat(
    party_name, chat_text, previous_messages, infer_chat_mode_flag, stream=False
):
    party = political_party_manager.get(party_name)
    # TODO: Should we use ChatMode.BEST??

    out = query_rewrite(chat_text, previous_messages, service_context)

    conversation = Conversation(
        (
            infer_chat_mode(chat_text, previous_messages)
            if infer_chat_mode_flag
            else ChatMode.CONTEXT
        ),
        party=party,
        similarity_top_k=SIMILARITY_TOP_K,
        system_prompt=system_prompt_specific_party(
            full_name=party.full_name, name=party.name
        ),
        node_postprocessors=[ExcludeMetadataKeysNodePostprocessor()],
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

    return answer, references


def infer_chat_mode(chat_text, previous_messages):
    conversation = Conversation(
        ChatMode.SIMPLE,
        previous_messages_token_limit=TOKEN_LIMIT,
        service_context=service_context,
    )

    raw_answer = conversation.chat(
        DECISION_TEMPLATE.format(message=chat_text), []
    )  # CAN BE CHANGED TO IMPROVE PERFORMANCE

    chat_mode = raw_answer.response

    if chat_mode in (ChatMode.SIMPLE, ChatMode.CONTEXT):
        return chat_mode

    return ChatMode.CONTEXT


def query_rewrite(query: str, previous_messages: list, service_context: ServiceContext):

    query_gen_str = """
    És um assistente cujo trabalho é reescrever a pergunta do utilizador para que seja mais fácil de pesquisar no nosso sistema, deves usar maioritariamente keywords e remover palavras de ligação.
    Deves ter em atenção ao histórico de mensagens abaixo:

    {previous_messages}

    Se o utilizador fizer uma referência ao histórico (por exemplo: "repete o ponto x", "clarifica o último tópico"), repete o respetivo contexto relevante na nova pergunta.
    Pergunta do utilizador:

    {query}

    Nova pergunta:
    """

    query_gen_prompt = PromptTemplate(query_gen_str)

    previous_messages

    rewritten_q = service_context.llm.predict(
        query_gen_prompt, previous_messages=previous_messages, query=query
    )
    logging.info(f"Rewritten query: {rewritten_q}")

    return rewritten_q
