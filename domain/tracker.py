from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from domain.assigment import Assignment
from domain.chore import Chore
from domain.group import Group
from domain.user import User


class Tracker:
    """
    Менеджер, который хранит все сущности и предоставляет методы управления.
    В реальном приложении это мог бы быть слой доступа к БД.
    """

    def __init__(self):

        self._users: Dict[int, User] = {}
        self._groups: Dict[int, Group] = {}
        self._chores: Dict[int, Chore] = {}
        self._assignments: Dict[int, Assignment] = {}
        # простые счетчики id
        self._next_user_id = 1
        self._next_group_id = 1
        self._next_chore_id = 1
        self._next_assignment_id = 1

    # ---------- User API ----------
    def create_user(self, name: str) -> User:
        user = User(id=self._next_user_id, name=name)
        self._users[user.id] = user
        self._next_user_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def list_users(self) -> List[User]:
        return list(self._users.values())

    # ---------- Group API ----------
    def create_group(self, name: str) -> Group:
        g = Group(id=self._next_group_id, name=name)
        self._groups[g.id] = g
        self._next_group_id += 1
        return g

    def add_user_to_group(self, user_id: int, group_id: int) -> bool:
        user = self.get_user(user_id)
        group = self._groups.get(group_id)
        if not user or not group:
            return False
        group.add_user(user)
        return True

    def list_groups(self) -> List[Group]:
        return list(self._groups.values())

    # ---------- Chore API ----------
    def create_chore(
        self, title: str, description: Optional[str], created_by_user_id: Optional[int]
    ) -> Chore:
        chore = Chore(
            id=self._next_chore_id,
            title=title,
            description=description,
            created_by_user_id=created_by_user_id,
        )
        self._chores[chore.id] = chore
        self._next_chore_id += 1
        return chore

    def list_chores(self) -> List[Chore]:
        return list(self._chores.values())

    # ---------- Assignment API ----------
    def assign_chore(
        self,
        chore_id: int,
        group_id: int,
        to_user_id: int,
        by_user_id: int,
        due_date: Optional[date] = None,
    ) -> Optional[Assignment]:
        # проверки: chore, group, user должны существовать и пользователь должен быть в группе
        chore = self._chores.get(chore_id)
        group = self._groups.get(group_id)
        to_user = self._users.get(to_user_id)
        by_user = self._users.get(by_user_id)
        if not all([chore, group, to_user, by_user]):
            return None
        if to_user_id not in group.user_ids:
            # нельзя назначить пользователю из другой группы
            return None
            assignment = Assignment(
                id=self._next_assignment_id,
                chore_id=chore_id,
                group_id=group_id,
                assigned_to_user_id=to_user_id,
                assigned_by_user_id=by_user_id,
                due_date=due_date,
            )
        self._assignments[assignment.id] = assignment
        self._next_assignment_id += 1
        return assignment

    def list_assignments(
        self, group_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> List[Assignment]:
        results = list(self._assignments.values())
        if group_id is not None:
            results = [a for a in results if a.group_id == group_id]
        if user_id is not None:
            results = [a for a in results if a.assigned_to_user_id == user_id]
        return results

    def mark_assignment_done(self, assignment_id: int) -> bool:
        a = self._assignments.get(assignment_id)
        if not a:
            return False
        a.mark_done()
        return True

    def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        return self._assignments.get(assignment_id)
