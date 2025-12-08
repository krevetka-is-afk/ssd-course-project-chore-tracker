# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Ритуал перед PR

```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты

```bash
pytest -q
```

## CI

В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.
![CI](https://github.com/krevetka-is-afk/ssd-course-project-chore-tracker/actions/workflows/ci.yml/badge.svg)

Дополнительно: workflow `P11 - DAST (ZAP baseline)` запускается вручную либо на пушах в `main` и ветки `p11-*`; конкурентные запуски отменяются, чтобы не копить очереди.

Дополнительно: workflow `Security - IaC & Container (P12)` запускается вручную либо на пушах в `main` и ветки `p12-*` при изменении `Dockerfile`, IaC (`iac/`, `k8s/`, `deploy/`) или `security/**`; конкурентные запуски отменяются, чтобы не копить очереди.

## Контейнеры

```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

Lint & scan (local)

```bash
hadolint Dockerfile                # Dockerfile lint
trivy image --severity HIGH,CRITICAL -f json -o trivy-report.json secdev-app:local
```

## Эндпойнты

- `GET /health` → `{"status": "ok"}`
- `POST /chores/` — задание по дому – сущность
- `GET /chores/`
- `GET /chores/{chore_id}`
- `PATCH /chores/{chore_id}`
- `DELETE /chores/{chore_id}`

## Формат ошибок

Все ошибки — JSON-обёртка:

```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
