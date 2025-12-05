import uuid
from collections.abc import Mapping, Sequence
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def make_problem_detail(
    *,
    status: int,
    title: str,
    detail: str,
    type_: str | None = None,
    extra: Dict[str, Any] | None = None,
):
    correlation_id = uuid.uuid4().hex
    payload = {
        "type": type_ or "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": correlation_id,
    }
    if extra:
        payload.update({k: _sanitize_value(v) for k, v in extra.items()})
    return payload


def _sanitize_value(value: Any):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [_sanitize_value(item) for item in value]
    return repr(value)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    title = exc.__class__.__name__
    detail = str(exc.detail) if exc.detail is not None else title
    problem = make_problem_detail(status=exc.status_code, title=title, detail=detail)
    return JSONResponse(status_code=exc.status_code, content=problem)


async def validation_exception_handler(request: Request, exc: Exception):
    raw_errors = None
    if hasattr(exc, "errors") and callable(getattr(exc, "errors")):
        try:
            raw_errors = exc.errors()
        except Exception:
            raw_errors = None
    errors = raw_errors if raw_errors is not None else [{"msg": str(exc)}]
    sanitized = _sanitize_value(errors)
    problem = make_problem_detail(
        status=422,
        title="ValidationError",
        detail="Validation error",
        extra={"errors": sanitized},
    )
    return JSONResponse(status_code=422, content=problem)


async def generic_exception_handler(request: Request, exc: Exception):
    problem = make_problem_detail(
        status=500,
        title="InternalServerError",
        detail="Internal server error",
    )
    return JSONResponse(status_code=500, content=problem)
