from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from licitaciones.matching.prompts import (
    QUERY_GENERATOR_PROMPT,
    QUERY_SANITIZER_PROMPT,
    QUERY_SCORE_CALCULATOR_PROMPT,
)


class QueryGenerator:
    def __init__(self, query_llm: ChatOpenAI, fast_llm: ChatOpenAI):
        self.query_llm = query_llm
        self.fast_llm = fast_llm

        self.query_chain = (
            PromptTemplate.from_template(QUERY_GENERATOR_PROMPT)
            | self.query_llm
            | StrOutputParser()
            | RunnableLambda(lambda x: {"query": x})
            | PromptTemplate.from_template(QUERY_SANITIZER_PROMPT)
            | self.fast_llm
            | StrOutputParser()
            | RunnableLambda(lambda x: {"query": x})
            | PromptTemplate.from_template(QUERY_SCORE_CALCULATOR_PROMPT)
            | self.query_llm
            | StrOutputParser()
        )

    def generate_query(self, json_response: dict) -> str:
        result = self.query_chain.invoke({"document_json": json_response})
        return result.content
