from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.chunk import DocumentChunkResponse
from app.services.chunking import chunk_text
from app.services.embedding import generate_embeddings
import PyPDF2
import io


router = APIRouter(prefix="/api/v1", tags=["Documents"])


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
    db: AsyncSession = Depends(get_db)
):
    # extract text from uploaded file
    text = await extract_text(file)

    file_type = file.filename.split(".")[-1].lower()

    # save document metadata to DB
    document = Document(
        filename=file.filename,
        file_type=file_type,
        content=text
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # split text into small chunks
    chunks = chunk_text(text)

    # generate embeddings for all chunks at once
    embeddings = generate_embeddings(chunks)

    # save each chunk with its embedding to DB
    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_obj = Chunk(
            document_id=document.id,
            chunk_text=chunk,
            chunk_index=index,
            embedding=embedding
        )
        db.add(chunk_obj)

    await db.commit()

    return DocumentChunkResponse(
        document_id=document.id,
        filename=file.filename,
        total_chunks=len(chunks),
        message="document processed successfully"
    )
