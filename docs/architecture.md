# Architecture

## Overview

Smart Certificate Generator is a two-tier application:

- **Backend**: FastAPI (Python) REST API, SQLAlchemy ORM over SQLite, JWT auth,
  APScheduler for background automation, ReportLab for PDF generation.
- **Frontend**: React (Vite) SPA, Tailwind CSS, React Router, Axios, Recharts.

```
┌─────────────┐        HTTPS/JSON        ┌──────────────────┐
│   React SPA │ ───────────────────────▶ │   FastAPI backend │
│  (Vite/Tailwind)                        │                    │
└─────────────┘ ◀─────────────────────── └──────────────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                              SQLite DB    ReportLab PDF    SMTP (email)
                                                  │
                                            generated/certificates/
```

## Backend layers

- **`app/core`** — configuration (env vars), database session management,
  security (JWT + password hashing). No business logic.
- **`app/models`** — SQLAlchemy ORM models (source of truth for schema).
- **`app/schemas`** — Pydantic request/response models (API contract).
- **`app/api`** — FastAPI routers. Thin: validate input, call services,
  shape output. No business logic lives here.
- **`app/services`** — business logic. In particular:
  - `automation_service.py` is the **single source of truth** for
    eligibility detection and duplicate-prevention. Both the scheduled job
    and the "Run Automation Now" admin button call into this same service,
    so behavior never diverges between the two triggers.
  - `certificate_service.py` renders the PDF only — no DB writes.
  - `email_service.py` sends the email only — never raises, always
    returns a result object so callers can persist status.
  - `learning_calc.py` is the single place that computes an employee's
    total learning hours from `learning_records` — the API layer never
    trusts a client-supplied total.
- **`app/scheduler`** — APScheduler wrapper. Runs `automation_service` on
  an interval, guarded against duplicate scheduler instances.

## Key design decisions

### Idempotent automation
Running the automation job any number of times must not create duplicate
certificates. This is enforced twice:
1. **Application-level check** — before creating a certificate, we query
   for an existing certificate with the same `(employee_id, achievement_type,
   target_hours)`.
2. **Database-level `UniqueConstraint`** on the same three columns, as a
   backstop against race conditions.

### Never trust client-supplied totals
`Employee.total_learning_hours` is a cached/denormalized value, but it is
**only ever written** by `learning_calc.recalculate_employee_hours()`,
which sums `learning_records`. No API endpoint accepts this value directly
from a request body.

### Email failures never block certificate creation
If SMTP isn't configured, or sending fails, the certificate record is still
created and persisted with `email_sent = false` and a
`email_failure_reason`. Admins can retry via `/api/certificates/{id}/resend`.

### File security
Certificate PDFs are stored outside any static file mount. The only way to
retrieve one is `GET /api/certificates/{id}/download`, which checks that
the requesting user is either an admin or the certificate's owning
employee before streaming the file.

## Frontend structure

- **`src/pages`** — one file per route.
- **`src/layouts/AppLayout.jsx`** — sidebar + navbar shell, role-aware nav.
- **`src/context`** — `AuthContext` (current user, login/logout) and
  `ToastContext` (global notifications).
- **`src/services`** — `api.js` (Axios instance + JWT interceptor) and
  `resources.js` (one function per backend endpoint).
- **`src/components`** — shared primitives (Card, Modal, form inputs, etc).
