from src.state import State, StepType
from langchain_core.messages import AIMessage

class FinalizerNode:
    def __call__(self, state: State) -> dict:
        """Synthesize final response from all collected data."""
        plan = state.get("plan")
        steps = plan.steps if plan else []
        scratch = state.get("scratch", {})

        # Check if we had calculations and return that result
        if any(s.type == StepType.CALCULATE for s in steps):
            calc = scratch.get("calc_result")
            if calc is not None:
                return {"messages": [AIMessage(content=f"The result is {calc}.")]}

        # Pass through the latest AI message (e.g., clarifying question)
        messages = state.get("messages", [])
        for m in reversed(messages):
            if isinstance(m, AIMessage):
                return {"messages": [m]}

        # Fallback (should rarely trigger)
        return {"messages": [AIMessage(content="Could you clarify what you'd like to do?")]}