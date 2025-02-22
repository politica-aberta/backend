from pathlib import Path
from llama_index.core.indices import VectorStoreIndex, SummaryIndex
from llama_index.core.storage import StorageContext
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.prompts import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.postprocessor.cohere_rerank import CohereRerank
from globals import service_context

from . import parties
from constants import (
    DOCUMENTS,
    ELECTIONS,
)


class PoliticalParty:
    def __init__(
        self, party_name: str, index, summary_index: SummaryIndex | None = None
    ):
        self.name = party_name
        self.full_name = parties[party_name].get("full_name")
        self.coalition = parties[party_name].get("coalition")
        self.leader = parties[party_name].get("leader")
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
            path = Path(f"./docs/{self.name}/{doc}.pdf")
            desc = ELECTIONS[doc]
            # if not path.exists():
            #     path = Path(f"./docs/{self.name}/legislativas22.pdf")
            #     desc = "Legislativas de 2022"

            out = reader.load_data(
                file=path,
                extra_info={
                    "description": f"Programa eleitoral do {self.full_name} para as Eleições {desc}."
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

            # DEFAULT_REFINE_PROMPT = PromptTemplate(
            # DEFAULT_REFINE_PROMPT_TMPL, prompt_type=PromptType.REFINE
            # )

            # llama_index/llama_index/prompts/default_prompts.py

            text_qa_template = (
                f"O teu trabalho é ajudar o utilizador a encontrar informação sobre o programa político do {self.name} ({self.full_name}), liderado por {self.leader}{(', que é uma coligação dos partidos ' + ' e '.join(self.coalition)) if self.coalition else ''}.\n"
                "O seguinte contexto contém excertos do programa eleitoral potencialmente relacionados.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Dado o contexto anterior, responde de forma fiel à seguinte pergunta do utilizador. Evita reproduzir contexto que nao seja diretamente relevante para a pergunta.\n"
                "Pergunta: Quais são as medidas/ideias do partido sobre o seguinte tópico: {query_str}\n"
                "Resposta: "
            )

            cohere_rerank = CohereRerank(
                model="rerank-multilingual-v2.0",
                top_n=4,
            )

            self.tool = QueryEngineTool(
                query_engine=self.index.as_query_engine(
                    similarity_top_k=16,
                    node_postprocessors=[cohere_rerank],
                    text_qa_template=PromptTemplate(
                        text_qa_template, prompt_type=PromptType.CUSTOM
                    ),
                ),
                metadata=ToolMetadata(
                    name=f"ferramenta_{self.name}",
                    description=(
                        "Útil para questões relacionada com "
                        f"o programa político do partido {self.full_name} ({self.name}), liderado por {self.leader}{(', que é uma coligação dos partidos ' + ' e '.join(self.coalition)) if self.coalition else ''}."
                    ),
                ),
            )
        else:
            raise Exception("Unable to create agent for " + self.name)
