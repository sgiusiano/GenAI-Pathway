from typing import TypedDict, Annotated, List, Dict, Any, Set
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import operator


def overwrite(left, right):
    """Overwrite left value with right value"""
    return right


def merge_dict(left: Dict[str, Any] | None, right: Dict[str, Any] | None) -> Dict[str, Any]:
    """Merge two dictionaries, handling None values"""
    return {**(left or {}), **(right or {})}


def merge_set(left: Set[str] | None, right: Set[str] | None) -> Set[str]:
    """Merge two sets, handling None values"""
    return (left or set()) | (right or set())


class AgentState(TypedDict):
    """Enhanced state for BizLaunch multi-agent system"""

    # Message history for audit trail
    messages: Annotated[List[BaseMessage], add_messages]

    # Original user input
    input: str

    # Current execution tracking
    current_agent: Annotated[str | None, overwrite]
    completed_agents: Annotated[Set[str], merge_set]

    # Iteration control
    iteration: Annotated[int, operator.add]
    max_iterations: int

    # Counters for monitoring
    tool_calls: Annotated[int, operator.add]
    retries: Annotated[int, operator.add]

    # Temporary data storage
    scratch: Annotated[Dict[str, Any], merge_dict]

    # Error tracking
    errors: Annotated[List[str], list.__add__]

    # Analysis results from each agent
    location_analysis: Annotated[str | None, overwrite]
    market_analysis: Annotated[str | None, overwrite]
    legal_analysis: Annotated[str | None, overwrite]

    # Final outputs
    final_report: Annotated[str | None, overwrite]
    clarification_needed: Annotated[str | None, overwrite]
