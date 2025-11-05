from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, SQLModel, create_engine, select

from app.chore import Chore, ChoreRead, ChoreUpdate, ChoreWrite

# ===--- db moment ---===
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(title="Chore Tracker", version="0.1.0")


# @app.on_event("startup")
def on_startup():
    create_db_and_tables()


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize FastAPI HTTPException into our error envelope
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


# ===--- endpoints moment ---===
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chores/", response_model=ChoreRead, status_code=201)
def create_chore(chore: ChoreWrite, session: SessionDep):
    db_obj = Chore(**chore.model_dump())
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@app.get("/chores/", response_model=List[ChoreRead])
def get_chores(
    session: SessionDep,
    limit: Annotated[int, Query(le=100)] = 100,
    offset: int = 0,
    name: Optional[str] = Query(default=None, description="substring match"),
    due_from: Optional[datetime] = Query(default=None),
    due_to: Optional[datetime] = Query(default=None),
):
    stmt = select(Chore)

    if name:
        stmt = stmt.where(Chore.name.contains(name))
    if due_from:
        if due_from.tzinfo is None:
            raise HTTPException(422, "due_from must include timezone")
        stmt = stmt.where(Chore.date_due >= due_from.astimezone(timezone.utc))
    if due_to:
        if due_to.tzinfo is None:
            raise HTTPException(422, "due_to must include timezone")
        stmt = stmt.where(Chore.date_due < due_to.astimezone(timezone.utc))

    stmt = stmt.offset(offset).limit(limit)
    chores = session.exec(stmt).all()
    return chores


@app.patch("/chores/{chore_id}", response_model=ChoreRead)
def update_chore(chore_id: int, payload: ChoreUpdate, session: SessionDep):
    db_obj = session.get(Chore, chore_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Chore not found")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_obj, k, v)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@app.delete("/chores/{chore_id}", status_code=204)
def delete_chore(chore_id: int, session: SessionDep):
    db_obj = session.get(Chore, chore_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Chore not found")
    session.delete(db_obj)
    session.commit()
    return JSONResponse(status_code=204, content=None)
