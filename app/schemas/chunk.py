from pydantic import BaseModel
from app.models.document import DocumentCategory 


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
    status: str              
    total_chunks: int
    message: str
    category: str

    # allows pydantic to read data from SQLAlchemy model objects
    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    document_id: int
    filename: str
    status: str
    total_chunks: int
    error_message: str | None = None
    category: str | None = None
    expected_chunks: int = 0 
    progress_percent: int = 0

    class Config:
        from_attributes = True
