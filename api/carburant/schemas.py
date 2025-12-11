from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class CarburantBase(BaseModel):
    libelle: str
    code: str


class CarburantCreate(CarburantBase):
    pass


class CarburantUpdate(CarburantBase):
    pass


class CarburantResponse(CarburantBase):
    id: UUID

    class Config:
        from_attributes = True


class CarburantGroupedByCompany(BaseModel):
    compagnie_id: UUID
    compagnie_nom: str
    carburants: List[CarburantResponse]