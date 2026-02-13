from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LegalAgent:
    def __init__(self, llm: ChatOpenAI, rag_tool):
        self.llm = llm
        self.rag_tool = rag_tool
        self.llm_with_tools = llm.bind_tools([rag_tool])

    def run(self, state: dict) -> dict:
        system_prompt = """
        You are a legal advisor specialized in business opening in Córdoba, Argentina.

        Your job is:
        1. Consult regulations using query_regulations (the tool accepts queries in Spanish since documents are in Spanish)
        2. Explain necessary taxes (AFIP, municipal, provincial)
        3. Detail commercial permit requirements
        4. Estimate timelines and costs for procedures

        Be clear and thorough with legal requirements.

        IMPORTANT: Always respond in the same language as the user's query.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["input"]),
        ]

        # Step 1: LLM decides to call RAG tool
        response = self.llm_with_tools.invoke(messages)

        tool_calls = []
        legal_context = ""

        # Step 2: Execute tool calls and collect context
        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = self.rag_tool.invoke(tool_call["args"])
                tool_calls.append({
                    "tool": tool_call["name"],
                    "args": tool_call["args"],
                    "result": result
                })
                legal_context += f"\n\n{result}"

        # Step 3: If we got tool results, generate final analysis with the context
        if legal_context:
            final_prompt = f"""
            Based on the following legal regulations and requirements:

            {legal_context}

            Provide a comprehensive legal analysis for the user's query: "{state["input"]}"

            Focus on:
            1. Necessary taxes (AFIP, municipal, provincial)
            2. Commercial permit requirements
            3. Specific regulations for this type of business
            4. Estimated timelines and costs for procedures
            5. Step-by-step process to get legally compliant

            IMPORTANT: Respond in the same language as the user's query.
            """

            final_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=final_prompt),
            ]

            final_response = self.llm.invoke(final_messages)
            analysis = final_response.content
        else:
            # No tool calls, use the original response
            analysis = response.content

        return {
            "legal_analysis": analysis,
            "tool_calls": tool_calls,
        }
