from pydantic import BaseModel

class DocumentBase(BaseModel):
    diploma_id: int
    ipfs_cid: str
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentRead(DocumentBase):
    document_id: int
    created_at: str
    model_config = {"from_attributes": True}
