# API Documentation

Base URL (local dev): `http://localhost:8000`

Interactive docs: `/docs` (Swagger UI) and `/redoc`.

All endpoints except `/api/auth/login`, `/`, and `/health` require a
`Authorization: Bearer <token>` header.

## Auth

| Method | Path              | Access | Description                |
|--------|-------------------|--------|------------------------------|
| POST   | `/api/auth/login` | Public | Returns a JWT access token   |
| GET    | `/api/auth/me`    | Any    | Returns the current user     |

## Dashboard

| Method | Path             | Access | Description                                          |
|--------|------------------|--------|--------------------------------------------------------|
| GET    | `/api/dashboard` | Any    | Admin summary cards/charts, or the caller's own progress if role=employee |

## Employees

| Method | Path                    | Access | Description                                  |
|--------|-------------------------|--------|-------------------------------------------------|
| GET    | `/api/employees`        | Admin  | List with `search`, `department`, `status`, `page`, `page_size` |
| POST   | `/api/employees`        | Admin  | Create employee (+ linked login user)           |
| GET    | `/api/employees/{id}`   | Admin, or the employee themself | Progress detail |
| PUT    | `/api/employees/{id}`   | Admin  | Update employee fields                          |
| DELETE | `/api/employees/{id}`   | Admin  | Deactivate (soft delete)                        |

## Courses

| Method | Path                  | Access | Description        |
|--------|-----------------------|--------|----------------------|
| GET    | `/api/courses`        | Any    | List, `search` param |
| POST   | `/api/courses`        | Admin  | Create course        |
| PUT    | `/api/courses/{id}`   | Admin  | Update course        |
| DELETE | `/api/courses/{id}`   | Admin  | Deactivate course    |

## Learning records

| Method | Path                                  | Access | Description                                             |
|--------|----------------------------------------|--------|------------------------------------------------------------|
| GET    | `/api/learning`                        | Admin  | All records                                                |
| POST   | `/api/learning`                        | Admin  | Create a record; recalculates the employee's total hours   |
| GET    | `/api/learning/employee/{employee_id}` | Admin, or that employee | Records for one employee                  |

## Certificates

| Method | Path                                  | Access | Description                                                 |
|--------|----------------------------------------|--------|------------------------------------------------------------------|
| GET    | `/api/certificates`                    | Any    | Admin sees all (optional `employee_id`/`certificate_id` filters); employees see only their own |
| GET    | `/api/certificates/{id}`               | Admin, or owning employee | Certificate metadata                        |
| GET    | `/api/certificates/{id}/download`      | Admin, or owning employee | Streams the PDF file                        |
| POST   | `/api/certificates/generate/{employee_id}` | Admin | Manually generate (400 if not eligible, 409 if duplicate) |
| POST   | `/api/certificates/{id}/resend`        | Admin  | Retry sending the certificate email                              |

## Automation

| Method | Path                     | Access | Description                                    |
|--------|--------------------------|--------|---------------------------------------------------|
| POST   | `/api/automation/run`    | Admin  | Runs the eligibility check + certificate generation immediately (safe to call repeatedly) |
| GET    | `/api/automation/status` | Admin  | Whether the scheduler is enabled, its interval, and last run summary |

## Settings

| Method | Path             | Access | Description                                         |
|--------|------------------|--------|--------------------------------------------------------|
| GET    | `/api/settings`  | Admin  | Current settings + whether SMTP is configured          |
| PUT    | `/api/settings`  | Admin  | Update target hours, automation interval, branding     |

## Error format

```json
{ "detail": "Human readable message" }
```

Validation errors (422) additionally include an `errors` array with
per-field details. Unhandled server errors return a generic 500 message —
no stack traces, credentials, or internal details are ever included in a
response body.
