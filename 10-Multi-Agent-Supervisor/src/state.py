from typing import TypedDict, Annotated, Any
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
import operator


def overwrite(left: Any, right: Any) -> Any:
    """Overwrite left value with right value"""
    return right


def merge_dict(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Merge two dictionaries"""
    return {**left, **right}


class WorkflowState(TypedDict):
    """Main workflow state for CX Support system"""
    messages: Annotated[list[BaseMessage], add_messages]
    route: Annotated[str | None, overwrite]
    scratch: Annotated[dict[str, Any], merge_dict]
    tool_calls: Annotated[int, operator.add]
    metrics: Annotated[dict[str, Any], merge_dict]
    stage: Annotated[str, overwrite]
    pending_approval: Annotated[bool, overwrite]


class SalesState(TypedDict):
    """State for Sales Specialist subgraph"""
    messages: Annotated[list[BaseMessage], add_messages]
    specialist_task: str
    available_tools: list[str]
    tool_scores: dict[str, float]
    execution_count: int
    scratch: Annotated[dict[str, Any], merge_dict]


class PostSalesState(TypedDict):
    """State for Post-Sales Specialist subgraph"""
    messages: Annotated[list[BaseMessage], add_messages]
    specialist_task: str
    available_tools: list[str]
    tool_scores: dict[str, float]
    execution_count: int
    ticket_id: str | None
    scratch: Annotated[dict[str, Any], merge_dict]
