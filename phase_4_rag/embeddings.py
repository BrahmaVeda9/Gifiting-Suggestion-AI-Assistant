import os
from dotenv import load_dotenv

load_dotenv()

def generate_embedding(text: str) -> list[float]:
    """Embedding stub — Groq does not provide an embeddings API.
    Returns an empty list; rag_pipeline and main.py handle this gracefully
    by returning fallback strategy cards."""
    print("[INFO] Groq does not support embeddings. Strategy matching will use fallback cards.")
    return []
