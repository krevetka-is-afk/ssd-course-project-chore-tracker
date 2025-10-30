from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import field_serializer
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


# ===--- model moment ---===
class ChoreBase(SQLModel):
    name: str = Field(index=True)
    date_created: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    date_due: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    # @field_validator("date_created", "date_due")
    # @classmethod
    # def must_be_tz_aware_and_utc(cls, v: datetime) -> datetime:
    #     if v.tzinfo is None:
    #         raise ValueError("datetime must include timezone (e.g., 2025-10-01T12:00:00+03:00)")
    #     return  v.astimezone(timezone.utc)


class Chore(ChoreBase, table=True):
    # id будет генерироваться в бд
    id: Optional[int] = Field(default=None, primary_key=True)


class ChoreWrite(ChoreBase):
    """Входная модель для POST /chores (без id)"""

    pass


class ChoreRead(ChoreBase):
    """Выходная модель"""

    id: int

    @field_serializer("date_created", "date_due")
    def serialize_dt(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


class ChoreUpdate(SQLModel):
    name: Optional[str] = None
    date_created: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    date_due: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # @field_validator("date_created", "date_due")
    # @classmethod
    # def must_be_tz_aware_and_utc_opt(cls, v: Optional[datetime]) -> Optional[datetime]:
    #     if v is None:
    #         return v
    #     if v.tzinfo is None:
    #         raise ValueError("datetime must include timezone")
    #     return v.astimezone(timezone.utc)
