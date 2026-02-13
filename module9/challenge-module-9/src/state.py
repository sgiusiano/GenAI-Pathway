from typing import Annotated, Any, Dict, List, TypedDict
from pydantic import BaseModel, Field
from enum import Enum
import operator

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

def merge_dict(old: Dict[str, Any] | None, new: Dict[str, Any] | None) -> Dict[str, Any]:
    return {**(old or {}), **(new or {})}

class StepType(str, Enum):
    """Types of steps the executor can perform"""
    SEARCH = "search"
    ANALYZE = "analyze"
    CALCULATE = "calculate"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    LOOKUP = "lookup"
    FACT_CHECK = "fact_check"

class PlanStep(BaseModel):
    """A single step in the plan"""
    description: str = Field(description="Description of what this step should do")
    type: StepType = Field(description="Type of step for the executor to use appropriate tool")
    success_criteria: str = Field(description="Criteria to determine if this step was successful")
    requires_interrupt: bool = Field(default=False, description="Whether this step requires human approval before execution")

class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[PlanStep] = Field(
        description="different steps to follow, should be in sorted order"
    )

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]       # audit trail
    plan: Plan                                                 # overwrite
    step_idx: int                                              # overwrite
    retries: Annotated[int, operator.add]                      # counter
    tool_calls: Annotated[int, operator.add]                   # counter
    scratch: Annotated[Dict[str, Any], merge_dict]             # shallow merge
    step_success: bool                                         # overwrite
    errors: Annotated[List[str], list.__add__]                 # append