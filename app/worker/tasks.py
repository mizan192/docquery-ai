from app.core.celery_app import celery_app
from app.core.logging import logger
from app.services.chunking import chunk_text
from app.services.embedding import generate_embeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings 
from app.models.document import Document, ProcessingStatus
from app.models.chunk import Chunk
import traceback
from app.services.extraction import extract_text


# sync engine for celery (celery does not support async db sessions)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
)
SyncSession = sessionmaker(sync_engine)


@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: int, file_content: bytes, file_type: str):
    """
    background task to chunk and embed document
    runs after document is uploaded to DB
    retries up to 3 times if it fails
    """
    logger.info(f"Background processing started: document_id={document_id}")
    
    with SyncSession() as db:
        # get document from DB
        document = db.get(Document, document_id)
        if not document:
            logger.warning(f"Document not found for document_id={document_id}")
            return

        try: 
            # mark as processing
            document.status = ProcessingStatus.PROCESSING
            db.commit()
            logger.info(f"Status set to PROCESSING: document_id={document_id}")

            # extract text in backgourd 
            if file_content: 
                document_text = extract_text(file_content, file_type)   
                document.content = document_text
                db.commit()
            else: 
                document_text = document.content
            
            if not document_text or not document_text.strip(): 
                document.status = ProcessingStatus.FAILED
                document.error_message = "No text extracted from file"
                db.commit()
                logger.warning(f"Failed: document_id={document_id} - No text extracted from file")
                return 

            # chunk the document text 
            chunks = chunk_text(document_text)
            logger.info(f"Chunking complete: document_id={document_id}, total_chunks={len(chunks)}")

            if not chunks:
                document.status = ProcessingStatus.FAILED
                document.error_message = "No chunks created from file"
                db.commit()
                logger.warning(f"Failed: document_id={document_id} - No chunks created from file")
                return

            # generate embeddings for all chunks 
            embeddings = generate_embeddings(chunks)
            logger.info(f"Embeddings generated: document_id={document_id}, total_embeddings={len(embeddings)}")

            # save chunks to DB 
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_obj = Chunk(
                    document_id=document.id,
                    chunk_text=chunk,
                    chunk_index=index,
                    embedding=embedding
                )
                db.add(chunk_obj)
                # commit every 20 chunks
                if index % 20 == 0:
                    db.commit()
            
            # update status to completed 
            document.status = ProcessingStatus.COMPLETED
            document.total_chunks = len(chunks)
            db.commit()

            logger.info(f"Background task completed: document_id={document_id}, chunks={len(chunks)}")
            
        except Exception as e:
            logger.warning(f"Background task failed for document_id={document_id}: {e}")
            logger.warning(traceback.format_exc())

            # rollback the failed transaction first, then mark as failed
            try:
                db.rollback()
                document = db.get(Document, document_id)  # re-fetch after rollback
                if document:
                    document.status = ProcessingStatus.FAILED
                    document.error_message = str(e)[:500]  # limit error message length
                    db.commit()
                    logger.info(f"Status set to FAILED: document_id={document_id}")
            except Exception as inner_e:
                logger.warning(f"Could not update status to FAILED: {inner_e}")

            # retry task if retries remaining
            try:
                raise self.retry(exc=e, countdown=60)
            except self.MaxRetriesExceededError:
                logger.warning(f"Max retries exceeded for document_id={document_id}. Giving up.")
