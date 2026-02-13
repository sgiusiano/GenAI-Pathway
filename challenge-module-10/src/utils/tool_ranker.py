"""Dynamic tool ranking and binding utility.

Implements the retrieve -> rank -> bind pattern for tool selection.
"""
import os

import numpy as np
from langchain_core.tools import BaseTool
from openai import OpenAI


class ToolRanker:
    """Ranks tools based on semantic similarity to the current task."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def rank_tools(
        self,
        task_description: str,
        tools: list[BaseTool],
        top_k: int = 3
    ) -> tuple[list[BaseTool], dict[str, float]]:
        """Rank tools by relevance to the task and return top-K."""
        task_embedding = self._get_embedding(task_description)

        tool_scores: dict[str, float] = {}
        for tool in tools:
            tool_text = f"{tool.name}: {tool.description}"
            tool_embedding = self._get_embedding(tool_text)
            score = self._cosine_similarity(task_embedding, tool_embedding)
            tool_scores[tool.name] = score

        sorted_tools = sorted(
            tools,
            key=lambda t: tool_scores[t.name],
            reverse=True
        )

        return sorted_tools[:top_k], tool_scores

    def rank_tools_simple(
        self,
        task_description: str,
        tools: list[BaseTool],
        top_k: int = 3
    ) -> tuple[list[BaseTool], dict[str, float]]:
        """Simplified ranking using keyword matching (fallback if embeddings fail)."""
        task_lower = task_description.lower()
        tool_scores: dict[str, float] = {}

        for tool in tools:
            score = 0.0
            tool_text = f"{tool.name} {tool.description}".lower()

            task_words = set(task_lower.split())
            tool_words = set(tool_text.split())

            intersection = len(task_words & tool_words)
            union = len(task_words | tool_words)

            if union > 0:
                score = intersection / union

            for word in task_words:
                if word in tool.name.lower():
                    score += 0.3

            tool_scores[tool.name] = min(score, 1.0)

        sorted_tools = sorted(
            tools,
            key=lambda t: tool_scores[t.name],
            reverse=True
        )

        return sorted_tools[:top_k], tool_scores


def bind_top_k_tools(
    task_description: str,
    all_tools: list[BaseTool],
    top_k: int = 3,
    use_embeddings: bool = True
) -> tuple[list[BaseTool], dict[str, float]]:
    """Retrieve -> Rank -> Bind pattern for dynamic tool selection."""
    ranker = ToolRanker()

    try:
        if use_embeddings:
            selected_tools, scores = ranker.rank_tools(
                task_description,
                all_tools,
                top_k
            )
        else:
            selected_tools, scores = ranker.rank_tools_simple(
                task_description,
                all_tools,
                top_k
            )
    except Exception as e:
        print(f"Warning: Embedding-based ranking failed ({e}), falling back to simple ranking")
        selected_tools, scores = ranker.rank_tools_simple(
            task_description,
            all_tools,
            top_k
        )

    return selected_tools, scores
