from src.state import State

class AdvanceCursorNode:
    def __call__(self, state: State) -> dict:
        """Advance to the next step and reset retries counter."""
        return {
            "step_idx": state.get("step_idx", 0) + 1,
            "retries": 0
        }