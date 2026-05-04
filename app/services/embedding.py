# services/embedding.py

from typing import List
from sentence_transformers import SentenceTransformer

# load model once when file is imported (not on every request)
# all-MiniLM-L6-v2 is fast, lightweight, and great for semantic search
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# this downloads the model on first run (~90MB), then caches it locally
model = SentenceTransformer(MODEL_NAME)


def get_embedding(text: str) -> List[float]:
    """
    Get embedding vector for a single text chunk.
    Returns a list of 384 floats.
    """
    # clean text
    text = text.replace("\n", " ").strip()

    # encode returns a numpy array — convert to plain list for pgvector
    embedding = model.encode(text)

    return embedding.tolist()


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple chunks in one batch.
    Much faster than calling one by one.
    Returns a list of vectors (each is a list of 384 floats).
    """
    # clean all texts
    texts = [t.replace("\n", " ").strip() for t in texts]

    # batch encode — sentence transformers handles this efficiently
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)

    # convert each numpy array to list
    return [emb.tolist() for emb in embeddings]
