from dataclasses import dataclass, field
from typing import List

from domain.group import Group


@dataclass
class User:
    id: int
    name: str
    # Мы храним список групп (идентификаторов) у пользователя для быстрого доступа
    group_ids: List[int] = field(default_factory=list)

    def join_group(self, group: Group):  # type: ignore[name-defined]
        if group.id not in self.group_ids:
            self.group_ids.append(group.id)
            group.add_user(self)

    def leave_group(self, group: Group):  # type: ignore[name-defined]
        if group.id in self.group_ids:
            self.group_ids.remove(group.id)
            group.remove_user(self)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"
