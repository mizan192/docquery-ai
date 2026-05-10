from sentence_transformers import SentenceTransformer
from typing import List


# load model once when app starts - downloads ~80MB on first run
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> List[float]:
    # generate embedding for single text chunk
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    # generate embeddings for all chunks at once (faster than one by one)
    embeddings = model.encode(chunks)
    return embeddings.tolist()
