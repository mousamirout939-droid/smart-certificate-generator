# Database Schema

SQLite for local development (via SQLAlchemy ORM); structured so switching
to PostgreSQL only requires changing `DATABASE_URL`.

## users

| Column         | Type      | Notes                              |
|----------------|-----------|-------------------------------------|
| id             | integer   | PK                                  |
| email          | string    | unique, indexed                     |
| password_hash  | string    | bcrypt hash, never plaintext        |
| role           | enum      | `admin` \| `employee`               |
| employee_id    | integer   | FK → employees.id, nullable (admins)|
| is_active      | boolean   |                                      |
| created_at     | datetime  |                                      |
| updated_at     | datetime  |                                      |

## employees

| Column                | Type     | Notes                                          |
|-----------------------|----------|-------------------------------------------------|
| id                    | integer  | PK                                              |
| employee_code         | string   | unique, indexed                                 |
| full_name             | string   |                                                  |
| email                 | string   | unique, indexed                                 |
| department            | string   | nullable                                        |
| designation           | string   | nullable                                        |
| joining_date          | date     | nullable                                        |
| target_hours          | float    | configurable per employee                       |
| total_learning_hours  | float    | **derived** — recalculated from learning_records|
| status                | enum     | `active` \| `inactive`                          |
| created_at            | datetime |                                                  |
| updated_at            | datetime |                                                  |

## courses

| Column          | Type     | Notes            |
|-----------------|----------|-------------------|
| id              | integer  | PK                |
| course_code     | string   | unique, indexed   |
| title           | string   |                   |
| description     | text     | nullable          |
| category        | string   | nullable          |
| duration_hours  | float    |                   |
| is_active       | boolean  |                   |
| created_at      | datetime |                   |

## learning_records

| Column                 | Type     | Notes                             |
|------------------------|----------|------------------------------------|
| id                     | integer  | PK                                 |
| employee_id            | integer  | FK → employees.id                  |
| course_id              | integer  | FK → courses.id                    |
| learning_hours         | float    | must be > 0                        |
| completion_percentage  | float    | 0–100                              |
| completion_date        | date     | nullable                           |
| status                 | enum     | `in_progress` \| `completed`       |
| created_at             | datetime |                                     |

## certificates

| Column                 | Type     | Notes                                            |
|------------------------|----------|----------------------------------------------------|
| id                     | integer  | PK                                                 |
| certificate_id         | string   | unique, indexed — e.g. `CERT-2026-8F4K92`          |
| employee_id            | integer  | FK → employees.id                                  |
| achievement_type       | string   | default `LEARNING_TARGET`                          |
| target_hours           | float    | target at time of issue                            |
| achieved_hours         | float    | hours achieved at time of issue                    |
| issue_date             | date     |                                                     |
| pdf_path               | string   | absolute path on disk, never exposed directly      |
| email_sent             | boolean  |                                                     |
| email_sent_at          | datetime | nullable                                           |
| email_failure_reason   | string   | nullable — populated when email_sent is false      |
| created_at             | datetime |                                                     |

**Unique constraint**: `(employee_id, achievement_type, target_hours)` —
this is the database-level backstop against duplicate certificate
generation, in addition to the application-level check in
`automation_service.py`.

## settings

| Column         | Type     | Notes                                    |
|----------------|----------|--------------------------------------------|
| id             | integer  | PK                                          |
| setting_key    | string   | unique, indexed — e.g. `CERTIFICATE_TARGET_HOURS` |
| setting_value  | string   |                                              |
| updated_at     | datetime |                                              |

## Relationships

```
users.employee_id ──────▶ employees.id      (1 user : 1 employee, for employee-role users)
learning_records.employee_id ──▶ employees.id
learning_records.course_id ──▶ courses.id
certificates.employee_id ──▶ employees.id
```
