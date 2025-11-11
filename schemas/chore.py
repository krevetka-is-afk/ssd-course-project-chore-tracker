from typing import Optional

from pydantic import BaseModel


class ChoreCreate(BaseModel):
    title: str
    description: Optional[str] = None
    # created_by_user_id опционально — если не указан,
    # будет заполнен текущим пользователем
    created_by_user_id: Optional[int] = None


class ChoreRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_by_user_id: Optional[int]

    class Config:
        orm_mode = True
