from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Literal
import json


class SupervisorAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def route(
        self, state: dict
    ) -> Literal["location", "market", "legal", "report", "ask_clarify", "end"]:
        """Decides which agent should be executed next using LLM."""

        # Check if max iterations reached
        if state.get("iteration", 0) >= state.get("max_iterations", 5):
            return "end"

        # Get completed agents from state
        completed_agents = state.get("completed_agents", set())

        # Check analysis completion (backward compatibility)
        has_location = "location" in completed_agents or state.get("location_analysis") is not None
        has_market = "market" in completed_agents or state.get("market_analysis") is not None
        has_legal = "legal" in completed_agents or state.get("legal_analysis") is not None
        has_report = "report" in completed_agents or state.get("final_report") is not None

        if has_report:
            return "end"

        user_input = state.get("input", "")

        if has_location and has_market and has_legal:
            return "report"

        system_prompt = """
        You are the supervisor of a multi-agent system that helps entrepreneurs launch businesses.

        You have these agents available:
        - ask_clarify: Asks user for clarification when query is unclear or missing critical information
        - location: Searches for commercial premises and analyzes locations (traffic, area, quality)
        - market: Analyzes market, demographics and competition in an area
        - legal: Consults legal requirements, taxes and commercial permits
        - report: Generates final report consolidating all analyses

        Analyses already completed:
        - Location: {"completed" if has_location else "pending"}
        - Market: {"completed" if has_market else "pending"}
        - Legal: {"completed" if has_legal else "pending"}

        ROUTING RULES (follow in order):
        1. If the query is NOT clear or NOT related to launching a business → "ask_clarify"
        2. If critical information is missing (business type, location, budget) → "ask_clarify"
        3. If ALL three analyses (location, market, legal) are completed → "report"
        4. If location is NOT completed and NOT in completed_agents → "location"
        5. If market is NOT completed and NOT in completed_agents → "market"
        6. If legal is NOT completed and NOT in completed_agents → "legal"
        7. If nothing left to do → "end"

        IMPORTANT CONSTRAINTS:
        - DO NOT route to an agent listed in completed_agents (see execution state below)
        - DO NOT route back to the agent that just executed (last_agent in execution state)
        - This is for internal routing only, do NOT respond to the user

        Return ONLY a JSON with this structure:
        {
        "next_agent": "ask_clarify|location|market|legal|report|end",
        "reason": "brief explanation"
        }
        """

        # Build comprehensive state context for routing decision
        current_agent = state.get("current_agent", "none")
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 5)
        tool_calls_count = state.get("tool_calls", 0)
        errors = state.get("errors", [])
        state_messages = state.get("messages", [])

        # Get analysis data availability
        location_available = "Yes" if state.get("location_analysis") else "No"
        market_available = "Yes" if state.get("market_analysis") else "No"
        legal_available = "Yes" if state.get("legal_analysis") else "No"

        # Format message history (last 5 messages for context)
        message_history = []
        for msg in state_messages[-5:]:
            msg_type = msg.__class__.__name__
            msg_content = str(msg.content)[:150] if hasattr(msg, 'content') else str(msg)[:150]
            message_history.append(f"[{msg_type}]: {msg_content}")

        messages_summary = "\n".join(message_history) if message_history else "No messages yet"

        # Build detailed context message
        context_message = f"""
        USER QUERY: {user_input}

        EXECUTION STATE:
        - Current iteration: {iteration}/{max_iterations}
        - Last agent executed: {current_agent}
        - Completed agents: {list(completed_agents) if completed_agents else []}
        - Total tool calls made: {tool_calls_count}
        - Errors encountered: {errors if errors else []}

        ANALYSIS DATA AVAILABILITY:
        - Location analysis: {location_available} (completed: {has_location})
        - Market analysis: {market_available} (completed: {has_market})
        - Legal analysis: {legal_available} (completed: {has_legal})

        RECENT MESSAGE HISTORY (last 5):
        {messages_summary}

        Based on this state and execution history, which agent should execute NEXT?
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context_message),
        ]

        response = self.llm.invoke(messages)
        content = response.content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            decision = json.loads(content)
            next_agent = decision.get("next_agent", "end")
        except json.JSONDecodeError:
            # If JSON parsing fails, default to end
            return "end"

        valid_routes = ["location", "market", "legal", "report", "ask_clarify", "end"]
        if next_agent not in valid_routes:
            return "end"

        return next_agent

    def should_continue(self, state: dict) -> bool:
        """Determines if the workflow should continue or end."""
        return state.get("final_report") is None
