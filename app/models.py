
from pydantic import BaseModel, HttpUrl

class Document(BaseModel):
    id: str
    name: str
    s3_url: HttpUrl