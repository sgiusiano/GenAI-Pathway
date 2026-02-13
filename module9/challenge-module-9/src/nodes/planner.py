from src.state import State, Plan, PlanStep, StepType
import random

class PlannerNode():
    
    def __call__(self, state: State) -> dict:
        """Create a plan with diverse random function calls simulating thinking."""

        # Set seed for deterministic randomness
        messages = state.get("messages", [])
        if messages:
            seed = hash(messages[-1].content) % 1000
            random.seed(seed)

        # Create pool of possible steps for diverse thinking
        possible_steps = [
            PlanStep(
                description="Analyze the user's question to understand information requirements",
                type=StepType.ANALYZE,
                success_criteria="Question intent and required information types are clearly identified",
                requires_interrupt=False
            ),
            PlanStep(
                description="Search knowledge base for relevant information",
                type=StepType.SEARCH,
                success_criteria="Relevant information retrieved from knowledge base",
                requires_interrupt=False
            ),
            PlanStep(
                description="Perform calculations on retrieved data",
                type=StepType.CALCULATE,
                success_criteria="Mathematical operations completed successfully",
                requires_interrupt=False
            ),
            PlanStep(
                description="Validate information accuracy and consistency",
                type=StepType.VALIDATE,
                success_criteria="Information verified for accuracy and consistency",
                requires_interrupt=True  # Critical step requiring human oversight
            ),
            PlanStep(
                description="Transform data into required format",
                type=StepType.TRANSFORM,
                success_criteria="Data successfully transformed to target format",
                requires_interrupt=False
            ),
            PlanStep(
                description="Lookup additional context from reference materials",
                type=StepType.LOOKUP,
                success_criteria="Relevant context retrieved from references",
                requires_interrupt=False
            ),
            PlanStep(
                description="Fact-check claims against reliable sources",
                type=StepType.FACT_CHECK,
                success_criteria="Claims verified against authoritative sources",
                requires_interrupt=True  # Critical verification step
            )
        ]

        # Randomly select 3-4 diverse steps to simulate dynamic thinking
        num_steps = random.randint(3, 4)
        plan_steps = random.sample(possible_steps, num_steps)

        # Create Plan object
        plan = Plan(steps=plan_steps)

        # Return partial state update
        return {
            "plan": plan,
            "step_idx": 0
        }
    