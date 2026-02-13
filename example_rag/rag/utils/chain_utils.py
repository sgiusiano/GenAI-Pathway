from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from rag.settings.constants import RETRIEVER_K, QA_CHAIN_TYPE
from rag.settings.prompt_templates import TEMPLATES_BY_NAME


class QAChainBuilder:
    def __init__(self,
                 prompt_template='default',
                 chain_type=QA_CHAIN_TYPE,
                 k=RETRIEVER_K,
                 search_type="similarity",
                 score_threshold=0.7,
                 fetch_k=20):

        self.prompt_template = TEMPLATES_BY_NAME.get(prompt_template, "")

        if not self.prompt_template:
            raise ValueError(f"Prompt template '{prompt_template}' not found.")

        self.search_type = search_type
        if self.search_type not in ["similarity", "similarity_score_threshold", "mmr"]:
            raise ValueError(f"Unsupported search type: {self.search_type}")

        self.chain_type = chain_type
        self.k = k
        self.score_threshold = score_threshold
        self.fetch_k = fetch_k
        
        self.search_kwargs = {"k": self.k}
        if self.search_type == "similarity_score_threshold":
            self.search_kwargs["score_threshold"] = self.score_threshold
        elif self.search_type == "mmr":
            self.search_kwargs["fetch_k"] = self.fetch_k or min(20, self.k * 3)


    def build_qa_chain(self, llm, vector_store):
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

        retriever = vector_store.as_retriever(
            search_type=self.search_type,
            search_kwargs=self.search_kwargs
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=self.chain_type,
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
