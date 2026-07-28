from app.services.chunking import chunk_text


def test_chunk_creates_chunks():
    """normal text should create chunks"""
    text = "word " * 300
    chunks = chunk_text(text)
    assert len(chunks) > 0


def test_chunk_empty_text():
    """empty text should return empty list"""
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_short_text():
    """short text should return single chunk"""
    text = "hello world this is short"
    chunks = chunk_text(text, chunk_size=500)
    assert len(chunks) == 1


def test_chunk_large_text_creates_multiple():
    """large text should create multiple chunks"""
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) > 1


def test_chunk_size_respected():
    """each chunk should not exceed chunk size by much"""
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=200)
    for chunk in chunks:
        # allow small overflow for word boundaries
        assert len(chunk) <= 250


def test_chunk_no_empty_chunks():
    """no chunk should be empty string"""
    text = "word " * 300
    chunks = chunk_text(text)
    for chunk in chunks:
        assert chunk.strip() != ""


def test_chunk_overlap():
    """overlap should create more chunks than without"""
    text = "word " * 500
    chunks_with_overlap = chunk_text(text, chunk_size=200, overlap=50)
    chunks_no_overlap = chunk_text(text, chunk_size=200, overlap=0)
    assert len(chunks_with_overlap) >= len(chunks_no_overlap)
