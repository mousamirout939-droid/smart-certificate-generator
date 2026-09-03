# Smart Certificate Generator

An employee learning-management system that **automatically** monitors
learning progress and issues a professional PDF certificate the moment an
employee reaches their learning target — no manual step required.

```
Employee completes 52 hours, target is 50 hours
        ↓
Automation detects the target was reached
        ↓
Unique certificate ID generated (CERT-2026-8F4K92)
        ↓
Professional PDF certificate rendered
        ↓
Certificate record saved (duplicate-proof)
        ↓
Emailed to the employee (or marked "Email Pending" if SMTP isn't configured)
        ↓
Visible on both the admin and employee dashboards, downloadable any time
```

## Features

- **Automatic eligibility detection** — a background scheduler (configurable
  interval) checks every active employee's learning hours against their
  target and issues certificates for anyone newly eligible.
- **Duplicate-proof** — running the automation any number of times never
  creates more than one certificate per employee/achievement. Enforced at
  both the application and database level.
- **Real, professional PDF certificates** — bordered, branded, with a
  signature area — generated with ReportLab, not a plain-text file.
- **Email delivery with graceful degradation** — if SMTP isn't configured,
  certificates still generate; they're marked "Email Pending" and can be
  resent later.
- **Role-based access** — Admins manage everything; employees can only ever
  see their own data and certificates.
- **Full admin dashboard** — stats, charts (learning progress, eligible vs.
  not, department breakdown), recent activity, and a "Run Automation Now"
  button for on-demand testing.
- **Employee self-service dashboard** — progress bar, remaining hours, and
  one-click certificate download once eligible.

## Tech stack

| Layer     | Technology                                                        |
|-----------|---------------------------------------------------------------------|
| Backend   | Python 3, FastAPI, SQLAlchemy, Pydantic, JWT auth, APScheduler      |
| Database  | SQLite (dev) — structured for a drop-in PostgreSQL swap later       |
| PDF       | ReportLab                                                            |
| Email     | SMTP (stdlib `smtplib`), credentials from environment variables only|
| Frontend  | React (Vite), Tailwind CSS, React Router, Axios, Recharts, Lucide   |
| Testing   | Pytest, FastAPI TestClient                                          |

## Folder structure

```
smart-certificate-generator/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, routers, lifespan, CORS
│   │   ├── core/                   # config, database, security
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── api/                    # route handlers
│   │   ├── services/                # business logic (automation, certs, email)
│   │   ├── scheduler/               # APScheduler job
│   │   ├── utils/                   # certificate ID generation, validators
│   │   └── seed.py                  # demo data
│   ├── generated/certificates/      # generated PDFs (not statically served)
│   ├── tests/                       # pytest suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/                         # React app (see frontend/README.md)
├── docs/
│   ├── architecture.md
│   ├── database-schema.md
│   └── api-documentation.md
└── README.md                        # you are here
```

## Quick start

### 1. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed          # creates demo data
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173.

## Demo credentials

All demo accounts use the password `Password123!`.

| Role     | Email                          | Learning hours | Target | Eligible? |
|----------|----------------------------------|-----------------|--------|-----------|
| Admin    | admin@example.com                | —               | —      | —         |
| Employee | rahul.sharma@example.com         | 52              | 50     | ✅ Yes     |
| Employee | priya.nair@example.com           | 68              | 50     | ✅ Yes     |
| Employee | arjun.mehta@example.com          | 32              | 50     | ❌ No      |
| Employee | sneha.iyer@example.com           | 45              | 50     | ❌ No      |
| Employee | vikram.rao@example.com           | 75              | 60     | ✅ Yes     |

This mix demonstrates eligible employees, non-eligible employees, and
different per-employee targets in the same demo dataset.

## Certificate generation & automation

- The **automation service** (`app/services/automation_service.py`) is the
  single source of truth for eligibility + duplicate prevention.
- It runs automatically every `AUTOMATION_INTERVAL_MINUTES` (default 30),
  via APScheduler.
- Admins can also trigger it on demand from the dashboard's
  **"Run Automation Now"** button, or `POST /api/automation/run`.
- Running it repeatedly is safe — verified by an automated test that runs
  it 10 times in a row and asserts exactly one certificate is created.

## SMTP / email setup

Set these in `backend/.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-address@gmail.com
SMTP_PASSWORD=your-app-password       # use a Gmail App Password, not your account password
SMTP_FROM=your-address@gmail.com
```

If left blank, the app runs fully functional without email: certificates
still generate and are marked **"Email Pending"** in the dashboard. An
admin can retry delivery any time from the Certificates page.

## Testing

```bash
cd backend
pytest -v
```

30 tests covering: login (valid/invalid), employee creation and duplicate
prevention, course creation, learning-hour calculation, target detection,
certificate generation, certificate ID uniqueness, duplicate-certificate
prevention (including a 10x-repeated-run check), certificate access
authorization (employees can't see each other's certificates), admin-only
endpoint authorization, and graceful handling when SMTP isn't configured.

## Swagger / API docs

With the backend running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Full endpoint reference: [`docs/api-documentation.md`](docs/api-documentation.md).

## Troubleshooting

- **"Invalid email or password" on login** — make sure you ran
  `python -m app.seed` and are using `Password123!`.
- **CORS errors in the browser console** — check `FRONTEND_URL` in
  `backend/.env` matches where the frontend is actually running.
- **Certificates stuck on "Email Pending"** — this is expected unless SMTP
  is configured (see above); it does not indicate a bug.
- **Port already in use** — change `--port` on the `uvicorn` command, and
  update `VITE_API_URL` in `frontend/.env` to match.

## Deployment notes

- Swap `DATABASE_URL` to a PostgreSQL connection string
  (`postgresql://user:pass@host/db`) and add `psycopg2-binary` to
  `requirements.txt` — no model or query code needs to change.
- Set a strong, random `JWT_SECRET` in production — never reuse the
  `.env.example` default.
- Put the frontend `dist/` behind a static host or CDN, and the backend
  behind a process manager (e.g. gunicorn + uvicorn workers) with HTTPS
  termination in front of it.
- Ensure `generated/certificates/` is on persistent storage (or an object
  store) in any containerized/ephemeral-filesystem deployment.

## Known limitations / not independently re-verified in this pass

- Load/performance testing at scale (hundreds of thousands of employees)
  was not performed; pagination exists on the employee list but very large
  deployments would benefit from database indexes review and possibly
  moving off SQLite.
- Email delivery was validated for the "SMTP not configured" and generic
  failure paths; an actual live SMTP send was not exercised end-to-end in
  this environment (no outbound SMTP network access here) — the code path
  is standard `smtplib` usage and was reviewed carefully, but you should
  do one live send test with real Gmail credentials before relying on it
  in production.
