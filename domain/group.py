from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from domain.user import User


@dataclass
class Group:
    id: int
    name: str
    user_ids: List[int] = field(default_factory=list)

    def add_user(self, user: User):
        if user.id not in self.user_ids:
            self.user_ids.append(user.id)
            if self.id not in user.group_ids:
                user.group_ids.append(self.id)

    def remove_user(self, user: User):
        if user.id in self.user_ids:
            self.user_ids.remove(user.id)
        if self.id in user.group_ids:
            user.group_ids.remove(self.id)

    def __repr__(self):
        return f"Group(id={self.id}, name={self.name})"
