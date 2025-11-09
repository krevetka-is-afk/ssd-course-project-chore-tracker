# Assignment(user_id, due_at, status)
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from domain.status import Status


@dataclass
class Assignment:
    id: int
    chore_id: int
    group_id: int
    assigned_to_user_id: int
    assigned_by_user_id: int
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[date] = None
    status: Status = Status.PENDING
    completed_at: Optional[datetime] = None

    def mark_done(self):
        self.status = Status.DONE
        self.completed_at = datetime.utcnow()

    def mark_skipped(self):
        self.status = Status.SKIPPED
        self.completed_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        if self.due_date and self.status == Status.PENDING:
            return date.today() > self.due_date
        return False

    def __repr__(self):
        return (
            f"Assignment(id={self.id}, chore_id={self.chore_id}, "
            f"to={self.assigned_to_user_id}, status={self.status})"
        )
