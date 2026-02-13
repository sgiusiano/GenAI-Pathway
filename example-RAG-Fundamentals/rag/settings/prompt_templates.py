# Prompt template
DEFAULT_TEMPLATE =  """
You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer the question.
If the answer is not in the context, say "I don't have enough information to answer this question."

Context:
{context}
        
Question: {question}
        
Answer:
"""


TEMPLATES_BY_NAME = {
    "default": DEFAULT_TEMPLATE
}
