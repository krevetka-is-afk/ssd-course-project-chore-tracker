from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

SQLITE_URL = "sqlite:///./chores.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# ---------------------------
# Ассоциационная таблица user <-> group (many-to-many)
# ---------------------------
group_users = Table(
    "group_users",
    Base.metadata,
    Column(
        "group_id",
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


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


# ---------------------------
# Pydantic (схемы запрос/ответ)
# ---------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserCreate(BaseModel):
    name: str = Field(..., example="Анна")
    password: str = Field(..., example="strongpassword")


class UserRead(BaseModel):
    id: int
    name: str
    group_ids: List[int] = []

    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    name: str = Field(..., example="Квартира на Невском")


class GroupRead(BaseModel):
    id: int
    name: str
    user_ids: List[int] = []

    class Config:
        orm_mode = True


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


# ---------------------------
# Dependency: DB session (reusable)
# ---------------------------


def get_db():
    """Yield a SQLAlchemy session (used as FastAPI dependency).

    Placing this in `domain.db` avoids circular imports (app.main imports domain.auth,
    and domain.auth needs a DB dependency). Other modules can import `get_db` from here.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
