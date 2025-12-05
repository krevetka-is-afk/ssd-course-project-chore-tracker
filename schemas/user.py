from typing import List

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(..., example="Анна")
    password: str = Field(..., example="strongpassword")


class UserRead(BaseModel):
    id: int
    name: str
    group_ids: List[int] = Field(default_factory=list)

    class Config:
        orm_mode = True
