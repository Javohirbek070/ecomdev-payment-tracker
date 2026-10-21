# Learning Center Payment Tracker

A production-grade, architectural technical assessment solution for tracking students, monthly tuition payments, and debtors at an educational center. Featuring a FastAPI REST API, persistent SQLite storage with SQLAlchemy 2.x ORM, exact monetary representation with Python's `Decimal`, strict Pydantic v2 validation, an administrative Telegram bot built on `aiogram 3.x` using `HTTPX`, and an isolated automated test suite with `pytest`.

---

## 1. Project Overview & Features

### Core Capabilities
- **Student Management (REST API)**: Full CRUD operations (`POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`) with strict validation (non-empty strings, whitespace stripping, positive monetary tuition fees, and automatic timestamps).
- **Accounting Deletion Policy**: Proactively blocks deleting students with existing payment history (HTTP 400 Bad Request) to preserve accounting integrity, auditability, and historical records.
- **Payment Processing**: Record tuition payments linked by foreign key (`student_id`), ensuring student existence, positive monetary amounts, valid payment dates, and referential integrity (`PRAGMA foreign_keys=ON`).
- **Exact Decimal Arithmetic**: Uses Python's `Decimal` and SQLAlchemy `Numeric(12, 2)` throughout business logic, database models, and validation schemas, completely eliminating binary floating-point rounding errors in monetary calculations.
- **Monthly Debtors Calculation**: `GET /debtors?month=YYYY-MM` dynamically calculates debtor status for any calendar month:
  - Exact calendar boundaries computed via `calendar.monthrange`.
  - Database aggregation (`outerjoin` with `func.sum`) grouping payments within the target month.
  - Compares aggregated payments against the student's current monthly fee: `debt = monthly_fee - total_paid`.
  - Excludes students who paid in full (`total_paid == monthly_fee`) or overpaid (`total_paid > monthly_fee`).
  - Includes non-paying students with `total_paid: 0.00` and `debt: monthly_fee`.
  - Rejects invalid month strings with **HTTP 422 Unprocessable Content**.
- **Telegram Bot (`aiogram 3.x` + `HTTPX`)**: Decoupled administrative bot communicating with the running FastAPI service:
  - Supports both **Local Long-Polling** and **Vercel Serverless Webhooks** (`POST /webhook/telegram`).
  - `/start`: Welcome guide and command instructions.
  - `/debt`: Summarizes debtors for the current calendar month with remaining debts.
  - `/pay <student_id> <amount>`: Records a tuition payment dated today (`date.today()`) via the REST API.
  - **Dual Role-Based Access Control (RBAC)**: Authorizes financial commands (`/pay`) via numeric Telegram User IDs (`TELEGRAM_ADMIN_IDS`) or Telegram usernames (`TELEGRAM_ADMIN_USERNAMES`, e.g. `@code_debugger007`, `@The_javohirbek`).
  - Safe error handling without leaking traceback traces to chat users.
- **Health Check**: `GET /health` and `GET /` endpoints for uptime monitoring and deployment health checks.
- **Automated Testing Suite**: 27 automated unit and integration tests executed against an isolated in-memory SQLite database (`StaticPool`), guaranteeing 0 side effects on production data.

---

## 2. Technology Stack

- **Python**: 3.11+ (Developed & tested on Python 3.12.0)
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (0.158+)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) (0.54+)
- **Database & ORM**: SQLite with [SQLAlchemy 2.x](https://www.sqlalchemy.org/) (2.1+)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) (2.13+) & [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Telegram Bot**: [aiogram 3.x](https://docs.aiogram.dev/) (3.31+)
- **HTTP Client**: [HTTPX](https://www.python-httpx.org/) (0.28+)
- **Testing**: [pytest](https://docs.pytest.org/) (8.4+) & [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- **Configuration**: [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 3. Architecture & Directory Structure

```text
ecomdev-payment-tracker/
├── app/
│   ├── __init__.py           # Package marker
│   ├── config.py             # Pydantic Settings configuration loader (.env)
│   ├── database.py           # Engine, SessionLocal, FK pragma, and Base
│   ├── models.py             # SQLAlchemy 2.0 ORM models (Student, Payment)
│   ├── schemas.py            # Pydantic v2 validation schemas with MoneyDecimal
│   ├── crud.py               # Data access layer and deletion policy
│   ├── exceptions.py         # Custom application exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── debtors.py        # Monthly debt aggregation service (Decimal)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── students.py       # /students CRUD endpoints
│   │   ├── payments.py       # /payments & /students/{id}/payments endpoints
│   │   └── debtors.py        # /debtors?month=YYYY-MM endpoint (HTTP 422 validation)
│   └── main.py               # FastAPI app factory, lifespan, and /health
├── bot/
│   ├── __init__.py
│   └── main.py               # aiogram 3.x bot dispatcher using HTTPX client
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # In-memory test engine, session, and TestClient
│   ├── test_students.py      # Student CRUD & deletion policy tests
│   ├── test_payments.py      # Payment creation & retrieval tests
│   ├── test_debtors.py       # Debt calculation & boundary test suite
│   └── test_bot.py           # Telegram bot commands, RBAC, and HTTPX tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (strictly excludes .env & *.db)
├── requirements.txt          # Python dependencies
├── vercel.json               # Serverless deployment configuration
├── main.py                   # Root entrypoint
└── README.md                 # Complete documentation
```

---

## 4. Prerequisites

- Python 3.11 or newer (`python --version`)
- Git (`git --version`)

---

## 5. Installation & Setup

### A. Windows 11 (PowerShell)

```powershell
# 1. Open PowerShell and navigate to the project directory
cd c:\Users\Lenovo\Desktop\job

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.venv\Scripts\Activate.ps1
# Note: If script execution is restricted on your machine, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
Copy-Item .env.example .env
```

### B. Linux / macOS (Bash / Zsh)

```bash
# 1. Navigate to the project directory
cd /path/to/project

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env
```

---

## 6. Environment Configuration

Edit the `.env` file created from `.env.example`:

```env
# Database configuration
DATABASE_URL=sqlite:///./learning_center.db

# API Server configuration
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=development

# Telegram Bot configuration
API_BASE_URL=http://127.0.0.1:8000
# Obtain your token from @BotFather on Telegram (e.g. 8744717265:AAHEnHE7d73OOfp1fbT6ChEyMhG_wqo6wU4)
TELEGRAM_BOT_TOKEN=8744717265:AAHEnHE7d73OOfp1fbT6ChEyMhG_wqo6wU4
# Comma-separated list of Telegram User IDs authorized to perform financial actions (/pay)
TELEGRAM_ADMIN_IDS=123456789
```

### How to Find Your Telegram User ID
1. In Telegram, start the bot `@userinfobot` or `@raw_data_bot`.
2. It will display your numeric User ID (e.g., `123456789`).
3. Add this ID to `TELEGRAM_ADMIN_IDS` in `.env`.
4. If an unauthorized user attempts `/pay`, the bot displays an Access Denied message containing their Telegram ID so administrators can easily whitelist them.

---

## 7. Database Initialization Behavior

- **Engine**: SQLite with SQLAlchemy 2.0 ORM.
- **Automatic Setup**: On startup, FastAPI's `lifespan` handler automatically invokes `init_db()`, creating all tables and indexes.
- **Integrity**: SQLite foreign key enforcement is explicitly activated on connection via `PRAGMA foreign_keys=ON`.
- **Persistence**: Data is saved to `learning_center.db` and persists across restarts.

---

## 8. How to Run

### 1. Start the FastAPI REST API
In your primary terminal:
```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Start the Telegram Bot
In a second terminal:
```powershell
.venv\Scripts\Activate.ps1
python -m bot.main
```
The bot connects to the running FastAPI server at `API_BASE_URL` (default `http://127.0.0.1:8000`) using `HTTPX`.

### 3. Run Automated Tests
```powershell
.venv\Scripts\Activate.ps1
pytest -v
```

---

## 9. API Reference & Examples

### Health Check
- `GET /health` or `GET /`
- Response: `{"status": "healthy", "service": "Learning Center Payment Tracker API", "documentation": "/docs"}`

---

### Student Management

#### 1. Create a Student
- **Endpoint**: `POST /students`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "name": "Ali Valiyev",
  "phone": "+998901234567",
  "group_name": "Python Beginner",
  "monthly_fee": 500000.0
}
```
- **Response**:
```json
{
  "id": 1,
  "name": "Ali Valiyev",
  "phone": "+998901234567",
  "group_name": "Python Beginner",
  "monthly_fee": 500000.0,
  "created_at": "2026-10-21T18:00:00",
  "updated_at": "2026-10-21T18:00:00"
}
```

#### 2. List Students
- **Endpoint**: `GET /students?skip=0&limit=100`
- **Status Code**: `200 OK`

#### 3. Retrieve Student by ID
- **Endpoint**: `GET /students/{student_id}`
- **Status Code**: `200 OK` (or `404 Not Found` if nonexistent)

#### 4. Update Student
- **Endpoint**: `PATCH /students/{student_id}`
- **Status Code**: `200 OK`
- **Request Body**: `{"monthly_fee": 550000.0}`

#### 5. Delete Student (with Accounting Deletion Policy)
- **Endpoint**: `DELETE /students/{student_id}`
- **If student has payments**: Returns **HTTP 400 Bad Request**:
```json
{
  "detail": "Cannot delete student with id 1: 1 payment record(s) exist. Deletion is restricted to preserve financial and accounting integrity."
}
```
- **If student has no payments**: Returns **HTTP 204 No Content**.

---

### Payment Management

#### 1. Record a Payment
- **Endpoint**: `POST /payments`
- **Status Code**: `201 Created`
- **Request Body**:
```json
{
  "student_id": 1,
  "amount": 300000.0,
  "payment_date": "2026-10-15"
}
```
- **Response**:
```json
{
  "id": 1,
  "student_id": 1,
  "amount": 300000.0,
  "payment_date": "2026-10-15",
  "created_at": "2026-10-21T18:05:00"
}
```

#### 2. List Student's Payment History
- **Endpoint**: `GET /students/{student_id}/payments`
- **Status Code**: `200 OK` (or `404 Not Found` if student does not exist)

---

### Monthly Debtors Endpoint

- **Endpoint**: `GET /debtors?month=YYYY-MM`
- **Example**: `GET /debtors?month=2026-10`
- **Status Code**: `200 OK`
- **Response**:
```json
{
  "month": "2026-10",
  "debtors": [
    {
      "student_id": 1,
      "name": "Ali Valiyev",
      "phone": "+998901234567",
      "group_name": "Python Beginner",
      "monthly_fee": 500000.0,
      "total_paid": 300000.0,
      "debt": 200000.0
    }
  ]
}
```

#### Business Rules
- **Date Boundaries**: Aggregates all payments whose `payment_date >= YYYY-MM-01` and `payment_date <= YYYY-MM-(last_day_of_month)`.
- **Current Fee Basis**: Debt is computed against the student's current monthly fee: `debt = monthly_fee - total_paid`.
- **Exclusion**: Fully paid (`total_paid == monthly_fee`) and overpaid (`total_paid > monthly_fee`) students are excluded.
- **Zero Payments**: Students who made 0 payments during the month are returned with `total_paid: 0.00` and `debt: monthly_fee`.
- **Invalid Month Format**: Returns **HTTP 422 Unprocessable Content** for malformed inputs (e.g. `2026-13`, `invalid`, `2026/10`).

---

## 10. Telegram Bot Commands

| Command | Arguments | Permission | Description |
| :--- | :--- | :--- | :--- |
| `/start` | None | Public | Welcome message and command instructions. |
| `/debt` | None | Public | Queries FastAPI `GET /debtors?month=YYYY-MM` and displays current month debtors. |
| `/pay` | `<student_id> <amount>` | Admins Only (`TELEGRAM_ADMIN_IDS` / `TELEGRAM_ADMIN_USERNAMES`) | Records payment via FastAPI `POST /payments` dated today (`date.today()`). Whitelisted for `@code_debugger007` and `@The_javohirbek`. |

---

## 11. Automated Test Results Observed

Executed with `pytest -v` against an isolated in-memory SQLite database:

```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-8.4.2, pluggy-1.7.0 -- .venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Lenovo\Desktop\job
plugins: anyio-4.15.1, asyncio-0.26.0

tests/test_bot.py::test_bot_authorization PASSED                         [  3%]
tests/test_bot.py::test_bot_start_command PASSED                         [  7%]
tests/test_bot.py::test_bot_pay_unauthorized PASSED                      [ 11%]
tests/test_bot.py::test_bot_pay_invalid_arguments PASSED                 [ 15%]
tests/test_bot.py::test_bot_pay_and_debt_with_httpx PASSED               [ 19%]
tests/test_bot.py::test_bot_handles_network_error PASSED                 [ 23%]
tests/test_debtors.py::test_debt_after_partial_payment PASSED            [ 26%]
tests/test_debtors.py::test_exclude_fully_paid_students PASSED           [ 30%]
tests/test_debtors.py::test_exclude_overpaid_students PASSED             [ 34%]
tests/test_debtors.py::test_aggregate_multiple_payments_in_one_month PASSED [ 38%]
tests/test_debtors.py::test_ignore_payments_outside_requested_month PASSED [ 42%]
tests/test_debtors.py::test_handle_month_with_no_payments PASSED         [ 46%]
tests/test_debtors.py::test_reject_invalid_month_formats PASSED          [ 50%]
tests/test_payments.py::test_record_payment_success PASSED               [ 53%]
tests/test_payments.py::test_reject_payment_for_nonexistent_student PASSED [ 57%]
tests/test_payments.py::test_reject_invalid_payment_amounts PASSED       [ 61%]
tests/test_payments.py::test_list_student_payment_history PASSED         [ 65%]
tests/test_payments.py::test_list_payments_nonexistent_student PASSED    [ 69%]
tests/test_students.py::test_create_student_success PASSED               [ 73%]
tests/test_students.py::test_list_and_retrieve_students PASSED           [ 76%]
tests/test_students.py::test_update_student PASSED                       [ 80%]
tests/test_students.py::test_handle_nonexistent_student PASSED           [ 84%]
tests/test_students.py::test_reject_invalid_monthly_fees PASSED          [ 88%]
tests/test_students.py::test_reject_empty_required_fields PASSED         [ 92%]
tests/test_students.py::test_delete_student_without_payments PASSED      [ 96%]
tests/test_students.py::test_delete_student_with_payment_history_blocked PASSED [100%]

======================= 26 passed in 9.42s =======================
```

---

## 12. Security & Quality Considerations

1. **No Hardcoded Secrets**: Secrets and tokens are loaded strictly via `pydantic-settings` from environment variables or `.env`. `.gitignore` excludes `.env`, `*.db`, and cache files.
2. **SQL Injection Prevention**: Built entirely with SQLAlchemy ORM and parameterized queries.
3. **RBAC on Financial Operations**: Telegram bot checks user ID authorization against `TELEGRAM_ADMIN_IDS` before executing payments.
4. **Resilient Error Suppression**: Database or external network connection failures are logged internally while users receive clear, sanitized error messages without stack traces.

---

## 13. Known Limitations

1. **Current Fee Calculation Rule**: Debt is evaluated against the student's *current* `monthly_fee`, as requested by the assignment specification. Historical fee rate changes will affect retrospective debt calculations.
2. **Single Currency**: Calculations assume a uniform currency (e.g. UZS). Multi-currency support is omitted to preserve simplicity.
3. **Telegram Long Polling**: The bot uses long polling (`start_polling`), which is optimal for single-process deployments but should be switched to Webhooks for multi-node deployments.

---

## 14. Realistic 1-Week Roadmap Improvements

1. **Historical Fee Schedule / Versioning**: Create a `StudentFeeRate` table recording `effective_from` dates so changes in tuition fees do not retroactively modify debtor calculations for prior months.
2. **Automated Telegram Reminders**: Use APScheduler or Celery with Redis to send automated debt reminders to students or administrators on the 1st and 15th of each month.
3. **JWT Authentication & Audit Logs**: Add OAuth2 with JWT to secure the REST API for multiple frontends (e.g. admin dashboard vs. cashier app) and log every payment creation with user identity.
4. **Soft Deletion & Student Status**: Add an `is_active` flag so graduated or withdrawn students can be archived without deleting their payment history.
5. **Excel / PDF Export**: Endpoints to export monthly financial ledger and debtor lists directly to XLSX or PDF.
