from typing import List

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str = Field(..., example="Квартира на Невском")


class GroupRead(BaseModel):
    id: int
    name: str
    user_ids: List[int] = Field(default_factory=list)

    class Config:
        orm_mode = True
