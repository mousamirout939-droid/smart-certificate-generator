# Backend — Smart Certificate Generator

FastAPI + SQLAlchemy + SQLite + ReportLab + APScheduler.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit values as needed
```

## Seed demo data

```bash
python -m app.seed
```

Creates 1 admin, 5 employees, 8 courses, and learning records. See the
root README for demo credentials.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Run tests

```bash
pytest -v
```

Tests use an isolated temp SQLite database and run with automation/SMTP
disabled, so they're fully offline and deterministic.

## Notes

- Certificates are written to `generated/certificates/` and are never
  served as static files — only through the authenticated
  `/api/certificates/{id}/download` endpoint.
- If `SMTP_HOST` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM` are left
  blank in `.env`, certificate generation still works; certificates are
  simply marked "Email Pending" until an admin retries via the resend
  endpoint (or SMTP is configured and automation runs again).
