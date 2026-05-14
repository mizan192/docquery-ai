from pydantic import BaseModel


# response schema for a single chunk
class ChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_text: str
    chunk_index: int

    # allows pydantic to read data from SQLAlchemy model objects
    class Config:
        from_attributes = True


# response schema after document is processed
class DocumentChunkResponse(BaseModel):
    document_id: int
    filename: str
    total_chunks: int
    message: str


class DocumentStatusResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    total_chunks: int
    error_message: str | None = None

    class Config:
        from_attributes = True
