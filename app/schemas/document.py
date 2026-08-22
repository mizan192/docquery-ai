from pydantic import BaseModel
from datetime import datetime


# ----------------------------------------
# Response schema
# what API returns after upload
# ----------------------------------------
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True  # read data from SQLAlchemy model
