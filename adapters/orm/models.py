from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from adapters.persistence import Base, engine
from domain.db import group_users

# ---------------------------
# Модели SQLAlchemy
# ---------------------------


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=False)
    hashed_password = Column(String, nullable=False)

    groups = relationship("GroupModel", secondary=group_users, back_populates="users")


class GroupModel(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    users = relationship("UserModel", secondary=group_users, back_populates="groups")


class ChoreModel(Base):
    __tablename__ = "chores"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_by = relationship("UserModel", foreign_keys=[created_by_user_id])


class AssignmentModel(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    chore_id = Column(Integer, ForeignKey("chores.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    assigned_to_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="pending", nullable=False)  # pending/done/skipped
    completed_at = Column(DateTime, nullable=True)

    chore = relationship("ChoreModel")
    group = relationship("GroupModel")
    assigned_to = relationship("UserModel", foreign_keys=[assigned_to_user_id])
    assigned_by = relationship("UserModel", foreign_keys=[assigned_by_user_id])


# Создаём таблицы (если не существуют)
Base.metadata.create_all(bind=engine)
