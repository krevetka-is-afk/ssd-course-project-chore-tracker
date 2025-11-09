from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Chore:
    id: int
    title: str
    description: Optional[str] = None
    created_by_user_id: Optional[int] = None

    def __repr__(self):
        return f"Chore(id={self.id}, title={self.title})"
