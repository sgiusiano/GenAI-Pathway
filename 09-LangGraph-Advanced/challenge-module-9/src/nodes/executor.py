from src.state import State, StepType
from langchain_core.messages import AIMessage
from src.tools.calculator import Calculator
from langgraph.errors import NodeInterrupt

class ExecutorNode:
    def __call__(self, state: State) -> dict:
        """Execute the current step based on its type."""

        # Get current plan and step
        plan = state["plan"]
        step_idx = state["step_idx"]

        if step_idx >= len(plan.steps):
            return {"step_success": False, "errors": ["No more steps to execute"]}

        current_step = plan.steps[step_idx]

        # Check if this step requires human approval (HITL)
        if current_step.requires_interrupt:
            # Check if human has already approved
            human_approved = state.get("scratch", {}).get("human_approved")
            if not human_approved:
                raise NodeInterrupt(f"Human approval required for: {current_step.description}")

        # Execute based on step type
        if current_step.type == StepType.ANALYZE:
            result = AIMessage(content=f"Analyzed: {current_step.description}")
            return {
                "messages": [result],
                "step_success": True
            }

        elif current_step.type == StepType.SEARCH:
            search_result = f"Search results for: {current_step.description}"
            result = AIMessage(content=search_result)
            return {
                "messages": [result],
                "scratch": {"search_data": search_result},
                "step_success": True
            }

        elif current_step.type == StepType.CALCULATE:
            # Use calculator tool to extract numbers and calculate
            calculator = Calculator()
            calc_result, calc_description = calculator.calculate(state.get("messages", []))
            result = AIMessage(content=f"Calculation completed: {calc_description}")
            return {
                "messages": [result],
                "scratch": {"calc_result": calc_result},
                "step_success": True
            }

        elif current_step.type == StepType.VALIDATE:
            result = AIMessage(content=f"Validation completed: {current_step.description}")
            return {
                "messages": [result],
                "scratch": {"validation_passed": True},
                "step_success": False
            }

        elif current_step.type == StepType.TRANSFORM:
            result = AIMessage(content=f"Data transformed: {current_step.description}")
            return {
                "messages": [result],
                "scratch": {"transform_result": "transformed_data"},
                "step_success": False
            }

        elif current_step.type == StepType.LOOKUP:
            lookup_result = f"Found context: reference_data_123"
            result = AIMessage(content=f"Lookup completed: {lookup_result}")
            return {
                "messages": [result],
                "scratch": {"lookup_data": lookup_result},
                "step_success": True
            }

        elif current_step.type == StepType.FACT_CHECK:
            result = AIMessage(content=f"Fact-check completed: {current_step.description}")
            return {
                "messages": [result],
                "scratch": {"fact_check_passed": True},
                "step_success": True
            }

        else:
            return {
                "step_success": False,
                "errors": [f"Unknown step type: {current_step.type}"]
            }