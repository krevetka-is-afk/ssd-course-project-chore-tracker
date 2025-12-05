from typing import List

from pydantic import BaseModel, ConfigDict, Field


class GroupCreate(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Квартира на Невском"})


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_ids: List[int] = Field(default_factory=list)
