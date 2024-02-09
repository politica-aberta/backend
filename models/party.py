from pathlib import Path
from llama_index import VectorStoreIndex, StorageContext, SummaryIndex
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.prompts import PromptTemplate



from . import parties
from globals import service_context
from constants import DOCUMENTS, ELECTIONS, system_prompt_specific_party


class PoliticalParty:
    def __init__(
        self, party_name: str, index, summary_index: SummaryIndex | None = None
    ):
        self.name = party_name
        self.full_name = parties[party_name]
        self.index = index
        self.summary_index = summary_index
        self.agent = None
        self.tool = None
        self.docs: list[Document] = []

    @staticmethod
    def docs_to_index(docs, storage_context: StorageContext):
        return VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            service_context=service_context,
            show_progress=True,
        )

    @staticmethod
    def docs_to_summary_index(docs) -> SummaryIndex:
        return SummaryIndex.from_documents(
            docs, service_context=service_context, show_progress=True
        )

    def generate_index(self, storage_context: StorageContext):
        index = self.docs_to_index(docs=self.docs, storage_context=storage_context)
        self.index = index

    def generate_summary_index(self):
        if not self.docs:
            raise Exception("no docs found!")
        summary_index = self.docs_to_summary_index(
            docs=self.docs,
        )
        self.summary_index = summary_index

    def import_party_files(self, reader: BaseReader):
        self.docs = []
        for doc in DOCUMENTS:
            out = reader.load_data(
                file=Path(f"./docs/{self.name}/{doc}.pdf"),
                extra_info={
                    "description": f"Programa eleitoral do {self.full_name} para as Eleições {ELECTIONS[doc]}."
                },
            )
            self.docs.extend(out)
        # for d in self.docs:
        #     d.metadata = {"year": 2022} # TODO do not hardcode year

    def set_agent(self):
        if self.index:  # and self.summary_index:
            # query_engine_tools = [
            #     QueryEngineTool(
            #         query_engine=self.index.as_query_engine(),
            #         metadata=ToolMetadata(
            #             name="ferramenta_vetores",
            #             description=(
            #                 "Útil para questões relacionada com "
            #                 f"o programa político do {self.full_name} ({self.name})."
            #             ),
            #         ),
            #     ),
            #     # QueryEngineTool(
            #     #     query_engine=self.summary_index.as_query_engine(),
            #     #     metadata=ToolMetadata(
            #     #         name="ferramenta_resumo",
            #     #         description=(
            #     #             "Útil para pedidos que requerem um resumo holístico"
            #     #             f"de TUDO sobre o programa político do {self.full_name} ({self.name})."
            #     #             " Para seccções mais específicas, por favor use o ferramenta_vetores."
            #     #         ),
            #     #     ),
            #     # ),
            # ]
            # self.agent = OpenAIAgent.from_tools(
            #     query_engine_tools,
            #     llm=LLM,
            #     verbose=True,
            #     system_prompt=system_prompt_specific_party(
            #         full_name=self.full_name, name=self.name
            #     ),
            # )

            # summary = (
            #     f"Este conteúdo contém o programa político do {self.full_name} ({self.name}). Usa"
            #     f" esta ferramenta se queres responder a alguma pergunta sobre o programa político do {self.full_name} ({self.name}).\n"
            # )

            # DEFAULT_REFINE_PROMPT_TMPL = (
            #     "The original query is as follows: {query_str}\n"
            #     "We have provided an existing answer: {existing_answer}\n"
            #     "We have the opportunity to refine the existing answer "
            #     "(only if needed) with some more context below.\n"
            #     "------------\n"
            #     "{context_msg}\n"
            #     "------------\n"
            #     "Given the new context, refine the original answer to better "
            #     "answer the query. "
            #     "If the context isn't useful, return the original answer.\n"
            #     "Refined Answer: "
            # )
            # from llama_index.prompts.prompt_type import PromptType

            # DEFAULT_REFINE_PROMPT = PromptTemplate(
            #     DEFAULT_REFINE_PROMPT_TMPL, prompt_type=PromptType.REFINE
            # )

            # llama_index/llama_index/prompts/default_prompts.py

            text_qa_template = (
                f"O teu trabalho é ajudar o utilizador a encontrar informação sobre o programa político do {self.name} ({self.full_name}).\n"
                "O seguinte contexto contém excertos do programa eleitoral.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Dado o contexto anterior, responde de forma fiel à seguinte pergunta do utilizador.\n"
                "Pergunta: Quais são as medidas/ideias do partido sobre o seguinte tópico: {query_str}\n"
                "Resposta: "
            )

            self.tool = QueryEngineTool(
                query_engine=self.index.as_query_engine(
                    text_qa_template=PromptTemplate(text_qa_template)
                ),
                metadata=ToolMetadata(
                    name=f"ferramenta_{self.name}",
                    description=(
                        "Útil para questões relacionada com "
                        f"o programa político do {self.full_name} ({self.name})."
                    ),
                ),
            )
        else:
            raise Exception("Unable to create agent for " + self.name)
