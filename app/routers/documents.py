from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
import PyPDF2
import io


router = APIRouter(prefix="/api/v1", tags=["Documents"])


# ----------------------------------------
# helper function - extract text from file
# ----------------------------------------
async def extract_text(file: UploadFile) -> str:
    content = await file.read()

    # if pdf - extract text using PyPDF2
    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    # if txt - decode directly
    elif file.filename.endswith(".txt"):
        return content.decode("utf-8")

    # other file types not supported
    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )


# ----------------------------------------
# upload endpoint
# ----------------------------------------
@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # extract text from uploaded file
    text = await extract_text(file)

    # get file type
    file_type = file.filename.split(".")[-1].lower()

    # save to database
    document = Document(
        filename=file.filename,
        file_type=file_type,
        content=text
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document
