from llama_index.chat_engine.types import ChatMode
import logging
from models.conversation import Conversation
from globals import political_party_manager, service_context
from constants import SIMILARITY_TOP_K, SYSTEM_PROMPT, TOKEN_LIMIT, DECISION_TEMPLATE
from postprocessor import ExcludeMetadataKeysNodePostprocessor


def process_chat(
    party_name, chat_text, previous_messages, infer_chat_mode_flag, stream=False
):
    party = political_party_manager.get(party_name)
    # TODO: Should we use ChatMode.BEST??
    if infer_chat_mode_flag:
        conversation = Conversation(
            infer_chat_mode(chat_text, previous_messages),
            party=party,
            similarity_top_k=SIMILARITY_TOP_K,
            system_prompt=SYSTEM_PROMPT,
            node_postprocessors=[ExcludeMetadataKeysNodePostprocessor()],
            previous_messages_token_limit=TOKEN_LIMIT,
            service_context=service_context,
        )

    else:
        conversation = Conversation(
            ChatMode.CONTEXT,
            party=party,
            similarity_top_k=SIMILARITY_TOP_K,
            system_prompt=SYSTEM_PROMPT,
            node_postprocessors=[ExcludeMetadataKeysNodePostprocessor()],
            previous_messages_token_limit=TOKEN_LIMIT,
        )

    if stream:
        raw_answer = conversation.stream_chat(chat_text, previous_messages)
        answer = raw_answer.response_gen

    else:
        raw_answer = conversation.chat(chat_text, previous_messages)
        answer = raw_answer.response

    def convert_file_format(path):
        """some docs have a file format of 'docs/{party}/legislativas22.pdf}
        while the supposed format is {party.lower()}/legislativas22.pdf}"""
        supabase_prefix = "https://dzwdgfmvuevjqjutrpye.supabase.co/storage/v1/object/public/documents/"
        tokens = path.split("/")
        path = f"{tokens[1].lower()}-{tokens[2]}" if len(tokens) == 3 else path
        return supabase_prefix + path

    pages = {}

    for node in raw_answer.source_nodes:
        if "file_name" in node.node.metadata:
            document = convert_file_format(node.node.metadata["file_name"])
            if document not in pages:
                pages[document] = set()

            if "page_label" in node.node.metadata:
                pages[document].add(int(node.node.metadata["page_label"]))

    references = [
        {
            "party": party_name,
            "document": document,
            "pages": list(pages),
        }
        for document, pages in pages.items()
    ]

    """ FIXME api is set as 
        {
            message: str,
            references:
                [{
                    party: str,
                    document: str -- url
                    pages: int[]
                }]
        }

        ie, aggregate by party, then by document
        this is a temporary fix, as we dont support either of these yet
    """
    logging.info(references)

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

    raise ValueError(f"Mode {chat_mode} does not exist")
