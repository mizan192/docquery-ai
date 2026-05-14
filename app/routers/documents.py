from app.schemas.chunk import DocumentStatusResponse
from app.models.document import ProcessingStatus
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.chunk import DocumentChunkResponse
from app.services.chunking import chunk_text
from app.services.embedding import generate_embeddings
from app.core.exceptions import InvalidFileType, FileTooLarge, EmptyDocument, DocumentNotFound
from app.core.logging import logger
import PyPDF2
import io
from app.models.user import User
from app.core.security import get_current_user 
from app.worker.tasks import process_document


router = APIRouter(prefix="/api/v1", tags=["Documents"])

# max file size 10MB
MAX_FILE_SIZE_MB = 12
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# allowed file types
ALLOWED_EXTENSIONS = [".pdf", ".txt"]

async def validate_file(file: UploadFile) -> bytes:
    # check file extension
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        raise InvalidFileType()

    # read file content
    content = await file.read()

    # check file size
    if len(content) > MAX_FILE_SIZE_BYTES:
        logger.warning(f"File too large: {file.filename} ({len(content)} bytes)")
        raise FileTooLarge(MAX_FILE_SIZE_MB)

    # check file is not empty
    if len(content) == 0:
        logger.warning(f"Empty file uploaded: {file.filename}")
        raise EmptyDocument()

    return content


async def extract_text(file: UploadFile) -> str:
    content = await file.read()

    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    elif file.filename.endswith(".txt"):
        return content.decode("utf-8")

    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )


@router.post("/documents/upload", response_model=DocumentChunkResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # extract text from uploaded file
    text = await extract_text(file)

    file_type = file.filename.split(".")[-1].lower()

    # save document metadata to DB with pending status 
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=file_type,
        content=text,
        status=ProcessingStatus.PENDING
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # NOTE: This code was moved to a Celery background task.
    # It’s commented out here because document chunking/embedding
    # now runs asynchronously via Redis workers instead of inline.

    # # split text into small chunks
    # chunks = chunk_text(text)
    # # generate embeddings for all chunks at once
    # embeddings = generate_embeddings(chunks)

    # # save each chunk with its embedding to DB
    # for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    #     chunk_obj = Chunk(
    #         document_id=document.id,
    #         chunk_text=chunk,
    #         chunk_index=index,
    #         embedding=embedding
    #     )
    #     db.add(chunk_obj)

    # await db.commit()
    # logger.info(f"Upload complete: document_id={document.id}, total_chunks={len(chunks)}")

    # NOTE : 
    # Send the task to Celery workers immediately so it runs in background.  
    # .delay() is shorthand for apply_async; use countdown for actual time delays.
    # user gets response right away without waiting
    process_document.delay(document.id)

    logger.info(f"Document queued for processing: id={document.id}")

    return DocumentChunkResponse(
        document_id=document.id,
        filename=file.filename,
        status=ProcessingStatus.PENDING,
        message="document uploaded successfully, processing in background"
    )


@router.post("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # check processing status of document 
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none() 

    if not document: 
        raise DocumentNotFound(document_id)
    
    chunk_count = await db.execute(
        select(func.count(Chunk.id)).where(Chunk.document_id == document_id)
    )
    total_chunks = chunk_count.scalar()

    return DocumentStatusResponse(
        document_id=document.id, 
        filename=document.filename,
        status=document.status,
        total_chunks=total_chunks,
        error_message=document.error_message
    )
