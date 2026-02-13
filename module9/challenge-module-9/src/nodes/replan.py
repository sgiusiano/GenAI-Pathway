from src.state import State, Plan, PlanStep, StepType

class ReplanNode:
    def __call__(self, state: State) -> dict:
        """Simple repair: collapse to a simpler explanation-only plan."""
        # Create a simple fallback plan with just analysis
        fallback_plan = Plan(steps=[
            PlanStep(
                description="Provide clarifying question or simple explanation",
                type=StepType.ANALYZE,
                success_criteria="Clear response provided to user",
                requires_interrupt=False
            )
        ])

        return {
            "plan": fallback_plan,
            "step_idx": 0,
            "retries": 0
        }