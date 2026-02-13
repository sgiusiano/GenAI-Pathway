from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LocationAgent:
    def __init__(self, llm: ChatOpenAI, tools: list):
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)

    def run(self, state: dict) -> dict:
        system_prompt = """You are an expert in commercial property search and location analysis.

Your job is:
1. Search for available properties using search_properties
2. Analyze each location using analyze_location
3. Recommend the best options considering the business type

Be specific and practical in your analysis.

IMPORTANT: Always respond in the same language as the user's query."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["input"]),
        ]

        response = self.llm_with_tools.invoke(messages)

        tool_calls = []
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool = next((t for t in self.tools if t.name == tool_call["name"]), None)
                if tool:
                    result = tool.invoke(tool_call["args"])
                    tool_calls.append(
                        {"tool": tool_call["name"], "args": tool_call["args"], "result": result}
                    )

        return {
            "location_analysis": response.content if not response.tool_calls else str(tool_calls),
            "tool_calls": tool_calls,
        }
