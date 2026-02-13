from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class AskClarifyAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, state: dict) -> dict:
        """Validates user query and asks for clarification if needed."""
        user_input = state.get("input", "")

        system_prompt = """You are a business launch assistant that validates user queries.

Your job is:
1. Analyze if the user query is clear and related to launching a business
2. Check if it contains necessary information (business type, location, or budget)
3. If the query is clear and complete, respond with EXACTLY: "CLEAR"
4. If information is missing or unclear, generate a friendly message asking for:
   - What type of business they want to open
   - In which area/location
   - Their approximate budget

Be friendly and helpful when asking for clarification.

IMPORTANT: Always respond in the same language as the user's query.
If the query is clear, respond ONLY with the word: CLEAR"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User query: {user_input}"),
        ]

        response = self.llm.invoke(messages)
        content = response.content.strip()

        # If query is clear, no clarification needed
        if content == "CLEAR":
            return {
                "clarification_needed": None,
            }

        # Query needs clarification
        return {
            "clarification_needed": content,
            "final_report": content,  # Show clarification message to user
        }
