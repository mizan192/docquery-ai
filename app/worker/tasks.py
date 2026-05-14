from app.models import document
from os import path
from app.models import document
from app.models import document
from app.core.celery_app import celery_app
from app.core.logging import logger
from app.services.chunking import chunk_text
from app.services.embedding import generate_embeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings 
from app.models.document import Document, ProcessingStatus
from app.models.chunk import Chunk


# sync engine for celery (celery does not support async db sessions)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
)
SyncSession = sessionmaker(sync_engine)

@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: int):
    """
    background task to chunk and embed document
    runs after document is uploaded to DB
    retries up to 3 times if it fails
    """
    logger.info(f"Background processing for document_id={document_id}")
    
    with SyncSession() as db:
        # get document from DB
        document = db.get(Document, document_id)
        if not document:
            logger.error(f"Document not found for document_id={document_id}")
            return

        try: 
            # mark as processing
            document.status = ProcessingStatus.PROCESSING
            db.commit()

            # chunk the document text 
            chunks = chunk_text(document.content)

            # generate embeddings for all chunks 
            embeddings = generate_embeddings(chunks)

            # save chunks to DB 
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_obj = Chunk(
                    document_id=document.id,
                    chunk_text=chunk,
                    chunk_index=index,
                    embedding=embedding
                )
                db.add(chunk_obj)
            
            # update status to completed 
            document.status = ProcessingStatus.COMPLETED
            db.commit()

            logger.info(f"Background task completed: document_id={document_id}")
            
        except Exception as e:
            # update status to failed and log the error
            document.status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()

            logger.error(f"Background task failed for document_id={document_id}: {e}")
            
            # retry task if failed 
            return self.retry(exc=e, countdown=60)
        
        

