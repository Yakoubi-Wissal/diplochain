from pydantic import BaseModel

class IPFSFileBase(BaseModel):
    cid: str
    status: str

class IPFSFileCreate(IPFSFileBase):
    pass

class IPFSFileRead(IPFSFileBase):
    file_id: int
    model_config = {"from_attributes": True}
