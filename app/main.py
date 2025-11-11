from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from adapters.orm.models import AssignmentModel, ChoreModel, GroupModel, UserModel
from adapters.persistence import get_db
from app.middleware.rate_limiter import SimpleRateLimiterMiddleware
from domain.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from domain.jwt import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.assignment import AssignmentCreate, AssignmentRead
from schemas.chore import ChoreCreate, ChoreRead
from schemas.groupe import GroupCreate, GroupRead
from schemas.token import Token
from schemas.user import UserCreate, UserRead

# ---------------------------
# FastAPI приложение
# ---------------------------
app = FastAPI(title="Household Chores Tracker (with Auth)", version="1.1")
app.add_middleware(SimpleRateLimiterMiddleware)


# ---------------------------
# Эндпойнты авторизации / регистрации
# ---------------------------
@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Проверим, нет ли уже пользователя с таким именем
    existing = db.query(UserModel).filter(UserModel.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this name already exists")
    hashed = get_password_hash(payload.password)
    user = UserModel(name=payload.name, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead(id=user.id, name=user.name, group_ids=[g.id for g in user.groups])


@app.post("/auth/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------
# Пользователи (чтение)
# ---------------------------
@app.get("/users/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).order_by(UserModel.id).all()
    result = []
    for u in users:
        result.append(UserRead(id=u.id, name=u.name, group_ids=[g.id for g in u.groups]))
    return result


@app.get("/users/me", response_model=UserRead)
def read_own_profile(current_user: UserModel = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        name=current_user.name,
        group_ids=[g.id for g in current_user.groups],
    )


# ---------------------------
# Группы (создание защищено)
# ---------------------------
@app.post("/groups/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    g = GroupModel(name=payload.name)
    db.add(g)
    db.commit()
    db.refresh(g)
    return GroupRead(id=g.id, name=g.name, user_ids=[u.id for u in g.users])


@app.get("/groups/", response_model=List[GroupRead])
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(GroupModel).order_by(GroupModel.id).all()
    result = []
    for g in groups:
        result.append(GroupRead(id=g.id, name=g.name, user_ids=[u.id for u in g.users]))
    return result


@app.post("/groups/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_user_to_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    g = db.get(GroupModel, group_id)
    u = db.get(UserModel, user_id)
    if not g or not u:
        raise HTTPException(status_code=404, detail="Group or User not found")
    if u in g.users:
        return
    g.users.append(u)
    db.commit()
    return


@app.delete("/groups/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    g = db.get(GroupModel, group_id)
    u = db.get(UserModel, user_id)
    if not g or not u:
        raise HTTPException(status_code=404, detail="Group or User not found")
    if u in g.users:
        g.users.remove(u)
        db.commit()
    return


# ---------------------------
# Chores (создание защищено)
# ---------------------------
@app.post("/chores/", response_model=ChoreRead, status_code=status.HTTP_201_CREATED)
def create_chore(
    payload: ChoreCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # если клиент не передал created_by_user_id — используем текущего пользователя
    created_by = payload.created_by_user_id or current_user.id
    # проверим, что указанный creator существует
    if created_by is not None and db.get(UserModel, created_by) is None:
        raise HTTPException(status_code=404, detail="Creator user not found")
    chore = ChoreModel(
        title=payload.title,
        description=payload.description,
        created_by_user_id=created_by,
    )
    db.add(chore)
    db.commit()
    db.refresh(chore)
    return ChoreRead(
        id=chore.id,
        title=chore.title,
        description=chore.description,
        created_by_user_id=chore.created_by_user_id,
    )


@app.get("/chores/", response_model=List[ChoreRead])
def list_chores(db: Session = Depends(get_db)):
    chores = db.query(ChoreModel).order_by(ChoreModel.id).all()
    return [
        ChoreRead(
            id=c.id,
            title=c.title,
            description=c.description,
            created_by_user_id=c.created_by_user_id,
        )
        for c in chores
    ]


# ---------------------------
# Assignments (создание защищено)
# ---------------------------
@app.post("/assignments/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    chore = db.get(ChoreModel, payload.chore_id)
    group = db.get(GroupModel, payload.group_id)
    to_user = db.get(UserModel, payload.assigned_to_user_id)
    if not chore or not group or not to_user:
        raise HTTPException(status_code=404, detail="chore/group/user not found")

    # Проверка: назначаемый должен быть в группе
    if to_user not in group.users:
        raise HTTPException(
            status_code=400,
            detail="User to be assigned is not a member of the specified group",
        )

    assigned_by = payload.assigned_by_user_id or current_user.id
    if db.get(UserModel, assigned_by) is None:
        raise HTTPException(status_code=404, detail="Assigned-by user not found")

    assign = AssignmentModel(
        chore_id=payload.chore_id,
        group_id=payload.group_id,
        assigned_to_user_id=payload.assigned_to_user_id,
        assigned_by_user_id=assigned_by,
        due_date=payload.due_date,
    )
    db.add(assign)
    db.commit()
    db.refresh(assign)
    return AssignmentRead(
        id=assign.id,
        chore_id=assign.chore_id,
        group_id=assign.group_id,
        assigned_to_user_id=assign.assigned_to_user_id,
        assigned_by_user_id=assign.assigned_by_user_id,
        assigned_at=assign.assigned_at,
        due_date=assign.due_date,
        status=assign.status,
        completed_at=assign.completed_at,
    )


@app.get("/assignments/", response_model=List[AssignmentRead])
def list_assignments(
    group_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(AssignmentModel)
    if group_id is not None:
        q = q.filter(AssignmentModel.group_id == group_id)
    if user_id is not None:
        q = q.filter(AssignmentModel.assigned_to_user_id == user_id)
    assignments = q.order_by(AssignmentModel.id).all()
    return [
        AssignmentRead(
            id=a.id,
            chore_id=a.chore_id,
            group_id=a.group_id,
            assigned_to_user_id=a.assigned_to_user_id,
            assigned_by_user_id=a.assigned_by_user_id,
            assigned_at=a.assigned_at,
            due_date=a.due_date,
            status=a.status,
            completed_at=a.completed_at,
        )
        for a in assignments
    ]


@app.post("/assignments/{assignment_id}/done", status_code=status.HTTP_204_NO_CONTENT)
def mark_assignment_done(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    a = db.get(AssignmentModel, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    a.status = "done"
    a.completed_at = datetime.utcnow()
    db.commit()
    return


@app.post("/assignments/{assignment_id}/skip", status_code=status.HTTP_204_NO_CONTENT)
def mark_assignment_skipped(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    a = db.get(AssignmentModel, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    a.status = "skipped"
    a.completed_at = datetime.utcnow()
    db.commit()
    return


# ---------------------------
# Health / root
# ---------------------------
@app.get("/")
def read_root():
    return {"message": "Household Chores Tracker — API. Документация: /docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
