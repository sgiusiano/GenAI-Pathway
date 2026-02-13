import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from bizlaunch.tools.mcp_tools import (
    search_properties,
    analyze_location,
    get_demographics,
    search_competitors,
)
from bizlaunch.tools.rag import LegalRAG, create_rag_tool
from bizlaunch.graph import BizLaunchGraph


class ApplicationContext:
    def __init__(self):
        load_dotenv()

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.docs_path = os.getenv("LEGAL_DOCS_PATH", "data/legal_docs")
        self.chroma_persist_path = os.getenv("CHROMA_PERSIST_PATH", "data/chroma_db")

        # LangSmith tracing is auto-enabled via environment variables:
        # LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

        self.llm = self._create_llm()
        self.rag = self._create_rag()
        self.rag_tool = create_rag_tool(self.rag)

        self.location_tools = [search_properties, analyze_location]
        self.market_tools = [get_demographics, search_competitors]

        self.graph = self._create_graph()

    def _create_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.model_name, temperature=0.7, api_key=self.openai_api_key, streaming=True
        )

    def _create_rag(self) -> LegalRAG:
        return LegalRAG(self.docs_path, persist_directory=self.chroma_persist_path)

    def _create_graph(self) -> BizLaunchGraph:
        return BizLaunchGraph(
            llm=self.llm,
            location_tools=self.location_tools,
            market_tools=self.market_tools,
            rag_tool=self.rag_tool,
        )

    def get_graph(self) -> BizLaunchGraph:
        return self.graph
