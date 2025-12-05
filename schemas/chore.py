from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChoreCreate(BaseModel):
    title: str
    description: Optional[str] = None
    # created_by_user_id опционально — если не указан,
    # будет заполнен текущим пользователем
    created_by_user_id: Optional[int] = None


class ChoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    created_by_user_id: Optional[int]
