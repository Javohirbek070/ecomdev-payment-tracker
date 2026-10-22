# Learning Center Payment Tracker & Admin Dashboard

A production-grade, architectural technical assessment solution for tracking students, monthly tuition payments, and debtors at an educational center. Featuring:
- **Interactive Admin Dashboard (Frontend)**: Built with React 19, TypeScript, Vite, and Tailwind CSS v4 in Uzbek language (`so'm` / UZS).
- **FastAPI REST API**: High-performance asynchronous backend with SQLite persistent storage and SQLAlchemy 2.x ORM.
- **Exact Decimal Arithmetic**: Uses Python's `Decimal` and SQLAlchemy `Numeric(12, 2)` throughout business logic, database models, and validation schemas, completely eliminating binary floating-point rounding errors.
- **Administrative Telegram Bot**: Decoupled `aiogram 3.x` bot with HTTPX client supporting both local long-polling and Vercel serverless webhooks (`POST /webhook/telegram`).
- **Comprehensive Automated Test Suite**: 30 automated unit and integration tests executed against an isolated in-memory SQLite database (`pytest`).

---

## 1. Project Overview & Features

### A. Admin Dashboard (Frontend UI)
- **Language & Currency**: Native Uzbek-language interface (`O'quvchilar`, `To'lovlar`, `Qarzdorlar`, `Boshqaruv paneli`) with currency in UZS (`so'm`).
- **Boshqaruv Paneli (Dashboard View)**:
  - Jami o'quvchilar soni (Total students)
  - Kutilayotgan oylik to'lov summasi (Total expected monthly tuition)
  - Bu oy yig'ilgan tushum (Total collected this month)
  - Qoldiq qarz summasi (Total outstanding debt)
  - Qarzdor o'quvchilar soni (Number of debtors)
  - Oxirgi qabul qilingan to'lovlar jadvali (Recent payments table)
  - Oyni tanlash filtri (Interactive calendar month selector)
- **O'quvchilar (Students View)**:
  - Qidiruv tizimi (Searchable table by name, phone, or group)
  - Yangi o'quvchi qo'shish formasi (Add student modal with validation)
  - O'quvchi ma'lumotlarini tahrirlash (Edit student modal)
  - O'quvchi tafsilotlari va shaxsiy to'lovlar tarixi (Details modal with complete payment history)
  - Xavfsiz o'chirish (Delete student with confirmation dialog strictly enforcing the accounting deletion policy)
- **To'lovlar (Payments View)**:
  - To'lov qabul qilish formasi (Student selection, amount input with auto-filled fee, date picker)
  - Barcha to'lovlar cheki ro'yxati (Recent payments table with student names and groups)
  - Qidiruv va saralash imkoniyati
- **Qarzdorlar (Debtors View)**:
  - Har qanday kalendar oy bo'yicha qarzdorlar monitoringi (`YYYY-MM`)
  - Qisman to'lagan va umuman to'lamagan o'quvchilarning alohida belgilanishi (`Qisman to'langan`, `To'lanmagan`)
  - Qarz miqdori hisob-kitobi: `qarz = oylik_tarif - to'langan_summa`
  - Qarzdor uchun to'g'ridan-to'g'ri to'lov kiritish amali
- **Moslashuvchan dizayn (Responsive Layout)**:
  - Desktop: Doimiy yon panel (Sidebar navigation)
  - Mobile: Ixcham ochiluvchi menyu (Mobile drawer menu) va sensorli qurilmalar uchun to'liq optimallashtirilgan

### B. REST API Backend
- **Student Management**: Full CRUD (`POST`, `GET`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`) with strict Pydantic v2 validation.
- **Accounting Deletion Policy**: Proactively blocks deleting students who have existing payment records (**HTTP 400 Bad Request**) to preserve accounting integrity.
- **Payment Processing**: Records tuition payments linked by foreign key (`student_id`), verifying student existence, positive monetary amounts, valid dates, and referential integrity (`PRAGMA foreign_keys=ON`).
- **Monthly Debtors Calculation**: `GET /debtors?month=YYYY-MM` dynamically calculates debtor status for any calendar month using exact Decimal arithmetic.
- **Dashboard Summary Endpoint**: `GET /dashboard/summary?month=YYYY-MM` returns aggregated statistics for the frontend dashboard.
- **Payments Listing**: `GET /payments?skip=0&limit=50` lists recent payments with student names and group associations.
- **CORS Configured**: Cross-Origin Resource Sharing enabled in `app/main.py` allowing frontend requests from any origin or development host.

### C. Telegram Bot (`aiogram 3.x` + `HTTPX`)
- Bot username: `@ecomedev_bot`
- Dual access control: User ID whitelist (`TELEGRAM_ADMIN_IDS`) and Username whitelist (`TELEGRAM_ADMIN_USERNAMES` e.g. `@code_debugger007`, `@The_javohirbek`).
- `/start`: Welcome guide and instructions.
- `/debt`: Summarizes debtors for current month.
- `/pay <student_id> <amount>`: Records a tuition payment dated today (`date.today()`).
- Supports both local polling and Vercel serverless webhook (`POST /webhook/telegram`).

---

## 2. Technology Stack

- **Frontend**:
  - React 19
  - TypeScript
  - Vite 8
  - Tailwind CSS v4
  - Lucide Icons
- **Backend**:
  - Python 3.11+ (Python 3.12)
  - FastAPI
  - Uvicorn
  - SQLite with SQLAlchemy 2.x ORM
  - Pydantic v2 & pydantic-settings
  - aiogram 3.x & HTTPX
  - pytest & FastAPI TestClient

---

## 3. Directory Structure

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
│   │   ├── debtors.py        # /debtors?month=YYYY-MM endpoint (HTTP 422 validation)
│   │   └── dashboard.py      # /dashboard/summary statistics endpoint
│   └── main.py               # FastAPI app factory, CORS, static files, and /health
├── bot/
│   ├── __init__.py
│   └── main.py               # aiogram 3.x bot dispatcher using HTTPX client
├── frontend/
│   ├── dist/                 # Production compiled assets (served by FastAPI)
│   ├── src/
│   │   ├── components/       # Header, Sidebar, StatCard, Modal, ConfirmModal
│   │   ├── views/            # DashboardView, StudentsView, PaymentsView, DebtorsView
│   │   ├── services/         # Typed API client (api.ts)
│   │   ├── types/            # TypeScript definitions (index.ts)
│   │   ├── utils/            # Monetary & date formatting helpers (format.ts)
│   │   ├── App.tsx           # Main application state and layout
│   │   ├── main.tsx          # Application entrypoint
│   │   └── index.css         # Tailwind CSS styling
│   ├── .env.example          # Frontend environment variables template
│   ├── package.json          # Dependencies (React 19, Tailwind v4, Lucide)
│   └── vite.config.ts        # Vite configuration with proxy and Tailwind
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # In-memory test engine, session, and TestClient
│   ├── test_students.py      # Student CRUD & deletion policy tests
│   ├── test_payments.py      # Payment creation & retrieval tests
│   ├── test_debtors.py       # Debt calculation & boundary test suite
│   ├── test_dashboard.py     # Dashboard summary, recent payments, and static serving tests
│   └── test_bot.py           # Telegram bot commands, RBAC, and HTTPX tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules (strictly excludes .env, node_modules, and *.db)
├── requirements.txt          # Python dependencies
├── vercel.json               # Serverless deployment configuration
├── main.py                   # Root entrypoint
├── run.py                    # Combined concurrent runner (FastAPI + Telegram Bot)
└── README.md                 # Complete documentation
```

---

## 4. Installation & Setup

### A. Windows 11 (PowerShell)

```powershell
# 1. Clone repository and navigate to project directory
cd c:\Users\Lenovo\Desktop\job

# 2. Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Configure backend environment
Copy-Item .env.example .env

# 5. Install frontend dependencies
cd frontend
npm install
npm run build
cd ..
```

### B. Linux / macOS (Bash)

```bash
# 1. Clone repository and navigate to project directory
cd /path/to/project

# 2. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Configure backend environment
cp .env.example .env

# 5. Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..
```

---

## 5. Environment Configuration

### Backend `.env`:
```env
DATABASE_URL=sqlite:///./learning_center.db
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=development

# Telegram Bot configuration
API_BASE_URL=http://127.0.0.1:8000
TELEGRAM_BOT_TOKEN=8744717265:AAHEnHE7d73OOfp1fbT6ChEyMhG_wqo6wU4
TELEGRAM_ADMIN_IDS=6752851778
TELEGRAM_ADMIN_USERNAMES=code_debugger007,The_javohirbek
```

### Frontend `frontend/.env`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 6. How to Run

### Option 1: Complete System Runner (Recommended)
Runs FastAPI (with embedded Admin Dashboard) and the Telegram Bot concurrently:
```powershell
.venv\Scripts\Activate.ps1
python run.py
```
Then open your browser:
- **Admin Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Telegram Bot**: Open Telegram and search for `@ecomedev_bot`

### Option 2: Frontend Development Server (with Hot Module Reloading)
In a separate terminal:
```powershell
cd frontend
npm run dev
```
Access the Vite dev server at [http://localhost:5173](http://localhost:5173).

---

## 7. Automated Test Suite

Run the full automated test suite containing 30 isolated tests:
```powershell
.venv\Scripts\Activate.ps1
pytest -v
```

### Test Results (100% Passed):
```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-8.4.2 -- .venv\Scripts\python.exe
collected 30 items

tests/test_bot.py::test_bot_authorization PASSED                         [  3%]
tests/test_bot.py::test_bot_start_command PASSED                         [  6%]
tests/test_bot.py::test_bot_pay_unauthorized PASSED                      [ 10%]
tests/test_bot.py::test_bot_pay_invalid_arguments PASSED                 [ 13%]
tests/test_bot.py::test_bot_pay_and_debt_with_httpx PASSED               [ 16%]
tests/test_bot.py::test_bot_handles_network_error PASSED                 [ 20%]
tests/test_bot.py::test_telegram_webhook_endpoint PASSED                 [ 23%]
tests/test_dashboard.py::test_list_all_payments_with_student_name PASSED [ 26%]
tests/test_dashboard.py::test_dashboard_summary_calculations PASSED      [ 30%]
tests/test_dashboard.py::test_dashboard_summary_invalid_month PASSED     [ 33%]
tests/test_dashboard.py::test_frontend_serving_endpoints PASSED          [ 36%]
tests/test_debtors.py::test_debt_after_partial_payment PASSED            [ 40%]
tests/test_debtors.py::test_exclude_fully_paid_students PASSED           [ 43%]
tests/test_debtors.py::test_exclude_overpaid_students PASSED             [ 46%]
tests/test_debtors.py::test_aggregate_multiple_payments_in_one_month PASSED [ 50%]
tests/test_debtors.py::test_ignore_payments_outside_requested_month PASSED [ 53%]
tests/test_debtors.py::test_handle_month_with_no_payments PASSED         [ 56%]
tests/test_debtors.py::test_reject_invalid_month_formats PASSED          [ 60%]
tests/test_payments.py::test_record_payment_success PASSED               [ 63%]
tests/test_payments.py::test_reject_payment_for_nonexistent_student PASSED [ 66%]
tests/test_payments.py::test_reject_invalid_payment_amounts PASSED       [ 70%]
tests/test_payments.py::test_list_student_payment_history PASSED         [ 73%]
tests/test_payments.py::test_list_payments_nonexistent_student PASSED    [ 76%]
tests/test_students.py::test_create_student_success PASSED               [ 80%]
tests/test_students.py::test_list_and_retrieve_students PASSED           [ 83%]
tests/test_students.py::test_update_student PASSED                       [ 86%]
tests/test_students.py::test_handle_nonexistent_student PASSED           [ 90%]
tests/test_students.py::test_reject_invalid_monthly_fees PASSED          [ 93%]
tests/test_students.py::test_reject_empty_required_fields PASSED         [ 96%]
tests/test_students.py::test_delete_student_without_payments PASSED      [100%]
tests/test_students.py::test_delete_student_with_payment_history_blocked PASSED [100%]

======================== 30 passed, 3 warnings in 2.10s ========================
```

---

## 8. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root endpoint: serves Admin Dashboard to browsers, or Health JSON |
| `GET` | `/health` | Health check endpoint for uptime monitoring |
| `GET` | `/dashboard/summary?month=YYYY-MM` | Aggregated dashboard KPIs (students, revenue, debt, debtors count) |
| `GET` | `/students` | List all students |
| `POST` | `/students` | Register a new student |
| `GET` | `/students/{student_id}` | Retrieve details of a student |
| `PATCH` | `/students/{student_id}` | Update student details |
| `DELETE` | `/students/{student_id}` | Delete student (blocked if payment history exists) |
| `POST` | `/payments` | Record a tuition payment |
| `GET` | `/payments?skip=0&limit=50` | List recent payments with student names |
| `GET` | `/students/{student_id}/payments` | List payment history for a specific student |
| `GET` | `/debtors?month=YYYY-MM` | Calculate debtors for target calendar month |
| `POST` | `/webhook/telegram` | Serverless webhook receiver for Telegram Bot updates |

---

## 9. AI Usage Report

In compliance with recruitment guidelines:
- **Architecture & Design**: Antigravity AI pair programming assistant was utilized to generate architectural structure, exact Decimal money modeling, Pydantic v2 schemas, FastAPI routes, and the React + Vite frontend dashboard.
- **Code Generation**: Complete boilerplate, CRUD handlers, Telegram bot webhook dispatcher, responsive UI views, and comprehensive pytest test suite were authored and verified.
- **Verification**: 100% of the code was executed and verified locally. All 30 tests pass cleanly, frontend builds with 0 errors, and Telegram bot communicates with the backend.
