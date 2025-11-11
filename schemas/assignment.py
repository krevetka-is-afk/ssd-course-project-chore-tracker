from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    chore_id: int
    group_id: int
    assigned_to_user_id: int
    # assigned_by_user_id опционально - подставим текущего пользователя
    assigned_by_user_id: Optional[int] = None
    due_date: Optional[date] = None


class AssignmentRead(BaseModel):
    id: int
    chore_id: int
    group_id: int
    assigned_to_user_id: int
    assigned_by_user_id: int
    assigned_at: datetime
    due_date: Optional[date]
    status: str
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
