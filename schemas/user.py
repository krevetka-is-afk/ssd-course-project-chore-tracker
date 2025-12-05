from typing import List

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Анна"})
    password: str = Field(..., json_schema_extra={"example": "strongpassword"})


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group_ids: List[int] = Field(default_factory=list)
