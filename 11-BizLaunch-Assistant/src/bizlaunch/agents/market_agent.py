from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class MarketAgent:
    def __init__(self, llm: ChatOpenAI, tools: list):
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)

    def run(self, state: dict) -> dict:
        system_prompt = """You are a market analyst specialized in local businesses.

Your job is:
1. Analyze the area demographics using get_demographics
2. Identify competitors using search_competitors
3. Evaluate market potential
4. Recommend differentiation strategies

Be realistic and data-driven.

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
            "market_analysis": response.content if not response.tool_calls else str(tool_calls),
            "tool_calls": tool_calls,
        }
