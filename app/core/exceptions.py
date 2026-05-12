from fastapi import HTTPException


class DocumentNotFound(HTTPException):
    # raised when document does not exist in DB
    def __init__(self, document_id: int):
        super().__init__(
            status_code=404,
            detail=f"Document with id {document_id} not found"
        )


class InvalidFileType(HTTPException):
    # raised when user uploads unsupported file type
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )


class FileTooLarge(HTTPException):
    # raised when uploaded file exceeds size limit
    def __init__(self, max_size_mb: int):
        super().__init__(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )


class EmptyDocument(HTTPException):
    # raised when uploaded file has no extractable text
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Document appears to be empty or has no extractable text"
        )


class NoChunksFound(HTTPException):
    # raised when search finds no relevant chunks
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="No relevant content found for your question"
        )
