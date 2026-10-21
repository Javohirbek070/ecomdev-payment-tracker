# Learning Center Payment Tracker

A production-minded mini-system for learning centers to manage students, record tuition payments, track monthly debtors, and automate notifications via an administrative Telegram bot. Built with FastAPI, SQLite, SQLAlchemy 2.x, Pydantic v2, and aiogram 3.x.

---

## 1. Project Overview & Features

### Core Capabilities
- **Student Management**: Full CRUD operations for student records with input validation (name, phone, group, positive monthly fee, and timestamps).
- **Payment Recording**: Ledger for tracking student tuition payments tied to specific payment dates.
- **Accounting-Safe Deletion Policy**: Prevents accidental deletion of students with existing payment history to maintain audit trail and ledger integrity.
- **Monthly Debtors Calculation**: Aggregates all student payments for any given calendar month (`YYYY-MM`), comparing total paid against the student's current monthly tuition fee, identifying partial payers and non-payers, while excluding fully-paid and overpaid students.
- **Telegram Bot Integration**: Administrative bot built with `aiogram 3.x` allowing authorized staff to query monthly debtors and record tuition payments directly from Telegram with instant validation and secure RBAC (Role-Based Access Control).
- **Comprehensive Automated Test Suite**: 100% test coverage across all critical business rules using an isolated in-memory SQLite database.

---

## 2. Technology Stack

- **Runtime**: Python 3.11+ (Tested on Python 3.12)
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/) (0.110+)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) (0.28+)
- **ORM & Database**: [SQLAlchemy 2.x](https://www.sqlalchemy.org/) with [SQLite](https://sqlite.org/) (Foreign key enforcement enabled)
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Telegram Bot Framework**: [aiogram 3.x](https://docs.aiogram.dev/)
- **Testing**: [pytest](https://docs.pytest.org/), [pytest-asyncio](https://pytest-asyncio.readthedocs.io/), and FastAPI `TestClient` (`httpx`)
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
│   ├── schemas.py            # Pydantic v2 validation schemas
│   ├── crud.py               # Data access layer and deletion policy
│   ├── exceptions.py         # Domain and application-level exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── debtors.py        # Monthly debt aggregation business logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── students.py       # /students CRUD endpoints
│   │   ├── payments.py       # /payments and /students/{id}/payments
│   │   └── debtors.py        # /debtors?month=YYYY-MM endpoint
│   └── main.py               # FastAPI app factory, lifespan, and routes
├── bot/
│   ├── __init__.py
│   └── main.py               # aiogram 3.x bot dispatcher and handlers
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # In-memory test engine, session, and TestClient
│   ├── test_students.py      # Student CRUD & deletion policy tests
│   ├── test_payments.py      # Payment creation & retrieval tests
│   ├── test_debtors.py       # Debt calculation & boundary test suite
│   └── test_bot.py           # Telegram bot commands & authorization tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation
```

---

## 4. Prerequisites

- Python 3.11 or newer (verify with `python --version` or `python3 --version`)
- Git (verify with `git --version`)

---

## 5. Installation & Setup

### A. Windows 11 (PowerShell)

```powershell
# 1. Clone the repository and navigate into the project directory
cd c:\Users\Lenovo\Desktop\job

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
.venv\Scripts\Activate.ps1
# If script execution is restricted, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 4. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### B. Linux / macOS (Bash / Zsh)

```bash
# 1. Navigate into the project directory
cd /path/to/project

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Environment Configuration

Copy `.env.example` to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

### Environment Variables Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLite database connection string | `sqlite:///./learning_center.db` |
| `API_HOST` | FastAPI host bind address | `127.0.0.1` |
| `API_PORT` | FastAPI port | `8000` |
| `ENVIRONMENT` | Runtime environment (`development`, `production`) | `development` |
| `TELEGRAM_BOT_TOKEN` | Bot API token from Telegram's `@BotFather` | *(Optional/Empty)* |
| `TELEGRAM_ADMIN_IDS` | Comma-separated Telegram User IDs authorized for `/pay` | *(Optional/Empty)* |

### How to Configure Telegram Bot
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts to create your bot name and username.
3. Copy the HTTP API token provided by BotFather.
4. Paste the token into your `.env` file: `TELEGRAM_BOT_TOKEN=123456789:ABCdef...`
5. To get your personal Telegram numeric User ID, open `@userinfobot` or `@raw_data_bot` in Telegram.
6. Add your User ID to `.env`: `TELEGRAM_ADMIN_IDS=123456789`

---

## 7. Database Initialization Behavior

- The application uses **SQLite** with **SQLAlchemy 2.0 ORM**.
- **Automatic Schema Initialization**: When the FastAPI server or the Telegram bot starts, the lifespan handler executes `init_db()`, which creates all required tables (`students`, `payments`) and indexes automatically if they do not exist.
- **Foreign Key Constraints**: SQLite by default disables foreign key enforcement. The application registers an engine connect hook that issues `PRAGMA foreign_keys=ON` on every SQLite connection.
- **Data Persistence**: Data is written to `learning_center.db` (or the path defined in `DATABASE_URL`) and persists across application restarts.

---

## 8. How to Run

### Running the REST API

Activate your virtual environment and run Uvicorn:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Linux / macOS:**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Running the Telegram Bot

Ensure `TELEGRAM_BOT_TOKEN` is set in `.env`, then execute:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
python -m bot.main
```

**Linux / macOS:**
```bash
source .venv/bin/activate
python -m bot.main
```

> **Note on Safety**: If `TELEGRAM_BOT_TOKEN` is missing or contains placeholder values, the bot will log an informative error and shut down cleanly without crashing other system services.

---

## 9. API Reference & Examples

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
  "created_at": "2026-10-21T18:00:00Z",
  "updated_at": "2026-10-21T18:00:00Z"
}
```

#### 2. List Students
- **Endpoint**: `GET /students?skip=0&limit=100`
- **Status Code**: `200 OK`

#### 3. Retrieve Student by ID
- **Endpoint**: `GET /students/{student_id}`
- **Status Code**: `200 OK` (or `404 Not Found` if not present)

#### 4. Update Student Details
- **Endpoint**: `PATCH /students/{student_id}`
- **Status Code**: `200 OK`
- **Request Body**:
```json
{
  "monthly_fee": 550000.0
}
```

#### 5. Delete Student (with Accounting Deletion Policy)
- **Endpoint**: `DELETE /students/{student_id}`
- **Status Code**: `204 No Content` (if no payments exist)
- **If Payments Exist**: Returns `400 Bad Request`
```json
{
  "detail": "Cannot delete student with id 1: 2 payment record(s) exist. Deletion is restricted to preserve financial and accounting integrity."
}
```

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
  "created_at": "2026-10-21T18:05:00Z"
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

#### Debt Calculation Business Rules
1. **Target Boundary**: Sums all payments where `payment_date >= YYYY-MM-01` and `payment_date <= YYYY-MM-(last_day_of_month)`.
2. **Current Fee Basis**: As specified, debt is computed against the student's *current* `monthly_fee`: `debt = monthly_fee - total_paid`.
3. **Exclusion**: Students who have paid in full (`total_paid == monthly_fee`) or overpaid (`total_paid > monthly_fee`) are excluded from the debtors list.
4. **Zero Payments**: Students who have made 0 payments during the month are reported with `total_paid: 0.0` and `debt: monthly_fee`.

---

## 10. Telegram Bot Commands

| Command | Arguments | Permissions | Description |
| :--- | :--- | :--- | :--- |
| `/start` | None | All Users | Displays welcome message and available command guide. |
| `/debt` | None | All Users | Lists debtors for the current calendar month with remaining balances. |
| `/pay` | `<student_id> <amount>` | Authorized Admins Only (`TELEGRAM_ADMIN_IDS`) | Records a tuition payment dated today (`date.today()`) for the student. |

### Example Bot Interactions
- `/pay 1 200000`
  - *Response*: `✅ Payment successfully recorded! Payment ID: #1 | Student: Ali Valiyev | Amount: 200,000.00 | Date: 2026-10-21`
- `/pay 999 150000`
  - *Response*: `❌ Student not found: No student exists with ID 999.`
- `/pay 1 -500`
  - *Response*: `❌ Invalid amount: Must be a positive number greater than 0.`
- Unauthorized user calling `/pay 1 100000`:
  - *Response*: `⛔ Access Denied: You are not authorized to perform financial operations.`

---

## 11. Automated Testing

All 16 required test scenarios, plus Telegram bot tests, are implemented using pytest with an in-memory SQLite database. Tests run in complete isolation and never modify the production database.

### Running Tests

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
pytest -v
```

**Linux / macOS:**
```bash
source .venv/bin/activate
pytest -v
```

### Test Scenarios Covered
1. `test_create_student_success`: Creating a student successfully.
2. `test_list_and_retrieve_students`: Listing and retrieving students.
3. `test_update_student`: Updating student details (PATCH).
4. `test_handle_nonexistent_student`: 404 responses for nonexistent student IDs.
5. `test_reject_invalid_monthly_fees`: Rejection of zero or negative tuition fees.
6. `test_record_payment_success`: Recording a payment successfully.
7. `test_reject_payment_for_nonexistent_student`: 404 response when recording payment for invalid student.
8. `test_list_student_payment_history`: Querying payment history for a student.
9. `test_debt_after_partial_payment`: Calculating debt after a partial payment.
10. `test_exclude_fully_paid_students`: Excluding students who paid the exact monthly fee.
11. `test_exclude_overpaid_students`: Excluding students who paid more than the monthly fee.
12. `test_aggregate_multiple_payments_in_one_month`: Summing multiple payments in the same calendar month.
13. `test_ignore_payments_outside_requested_month`: Ensuring payments from adjacent months do not bleed into the target month.
14. `test_handle_month_with_no_payments`: Listing students with `total_paid: 0` when no payments exist.
15. `test_reject_invalid_month_formats`: Returning 400 for malformed months (e.g. `2026-13`, `invalid`, `2026/10`).
16. `test_delete_student_with_payment_history_blocked`: Enforcing deletion policy that blocks deleting students with payment history.
17. Bot tests: `/start`, `/debt`, `/pay` argument validation, RBAC security, and DB integration.

---

## 12. Known Limitations

1. **Current Monthly Fee Rule**: As dictated by the assessment requirements, debt is calculated against the student's *current* `monthly_fee` rather than historical fee snapshots at the time of past months.
2. **Single Currency**: Monetary values are stored as floating-point / decimal numbers assuming a uniform currency (e.g., UZS).
3. **Bot Transport**: The Telegram bot operates via Long Polling (`start_polling`), which is ideal for development and single-instance deployments, but production at scale would use webhooks with reverse proxy SSL termination.

---

## 13. Realistic 1-Week Roadmap Improvements

If given one additional week of development time, the following production-grade enhancements would be implemented:

1. **Historical Tuition Fee Snapshotting**: Introduce a `FeeSchedule` or versioned contract model so that changes to a student's monthly fee do not retroactively alter the calculated debt for prior months.
2. **Automated Telegram Notifications & Webhooks**: Configure a background task runner (e.g., Celery with Redis or APScheduler) to automatically send scheduled debt reminders to debtors via Telegram on the 1st and 15th of every month, and switch the bot to Telegram Webhooks.
3. **Role-Based Authentication (JWT) & Audit Logs**: Add authentication (OAuth2 with JWT tokens) for API endpoints, distinguishing between read-only staff, cashiers, and administrators, accompanied by an audit log table recording every payment creation and student modification.
4. **Export & Reporting (CSV/Excel/PDF)**: Provide endpoints to export monthly debtor reports and financial balance sheets to Excel (`.xlsx`) or PDF for the accounting department.
5. **Soft Deletion & Archive Mode**: Implement an `is_active` / soft-delete flag for students so that graduated or withdrawn students can be deactivated without deleting their financial records.
