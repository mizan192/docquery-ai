from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from typing import List


# Uses transformers directly (same library as llm.py) — no sentence-transformers needed.
# SentenceTransformer is just a wrapper around this exact pattern (tokenize → encode → mean pool).
#
# Model is intentionally NOT loaded at module level.
# Celery forks workers from the parent process. If PyTorch models/tokenizers are
# loaded before the fork, the child inherits frozen mutex state → deadlock at inference.
# Lazy loading here ensures the model is created fresh inside each forked worker.

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_tokenizer: AutoTokenizer | None = None
_model: AutoModel | None = None


def _get_tokenizer_and_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
        _model = AutoModel.from_pretrained(EMBEDDING_MODEL)
        _model.eval()  # disable dropout for consistent embeddings
    return _tokenizer, _model


def _mean_pool(token_embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Average token embeddings, ignoring padding tokens."""
    mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * mask_expanded, dim=1) / torch.clamp(mask_expanded.sum(dim=1), min=1e-9)


def _encode(texts: List[str]) -> List[List[float]]:
    tokenizer, model = _get_tokenizer_and_model()

    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        output = model(**encoded)

    # mean pool over token dimension → one vector per text
    embeddings = _mean_pool(output.last_hidden_state, encoded["attention_mask"])

    # L2-normalize so cosine similarity = dot product (standard for retrieval)
    embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings.tolist()


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text chunk."""
    return _encode([text])[0]


def generate_embeddings(chunks: List[str], batch_size: int = 32) -> List[List[float]]:
    """Generate embeddings for all chunks in batches."""
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i: i + batch_size]
        all_embeddings.extend(_encode(batch))
    return all_embeddings
