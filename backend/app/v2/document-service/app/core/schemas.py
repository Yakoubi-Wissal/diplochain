from pydantic import BaseModel

from typing import Optional

class RapportBase(BaseModel):
    nom_documents: str
    id_langue: int
    id_type_impression: int
    id_annee: int
    etat: bool
    code_rapport: str

class RapportCreate(RapportBase):
    pass

class RapportRead(RapportBase):
    id_rapport: int
    model_config = {"from_attributes": True}
