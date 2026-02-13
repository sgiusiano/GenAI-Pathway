from src.state import State

class RetryNode:
    def __call__(self, state: State) -> dict:
        """Increment the retry counter for the current step."""
        return {"retries": 1}  # add=1