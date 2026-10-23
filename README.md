# Ecomdev — O'quv Markazi To'lovlarini Boshqarish Tizimi va Admin Dashboard

Ushbu loyiha o'quv markazlarida o'quvchilar ro'yxati, oylik to'lovlar, tushumlar va qarzdorliklarni hisobga olish hamda boshqarish uchun mo'ljallangan ishlab chiqarish darajasidagi (production-ready) to'liq tizimdir.

Loyiha quyidagi asosiy qismlarni o'z ichiga oladi:
- **Admin Dashboard (Veb interfeys)**: React 19, TypeScript, Vite va Tailwind CSS v4 asosida yaratilgan zamonaviy, to'liq o'zbek tilidagi va UZS (`so'm`) valyutasidagi boshqaruv paneli.
- **FastAPI REST API (Backend)**: Yuqori tezlikda ishlovchi asinxron backend, SQLite ma'lumotlar bazasi va SQLAlchemy 2.x ORM.
- **Aniq Decimal Arifmetikasi**: Moliyaviy hisob-kitoblarda yaxlitlash xatolarini (floating-point binary rounding errors) to'liq bartaraf etish uchun Python'ning `Decimal` va SQLAlchemy `Numeric(12, 2)` turlari ishlatilgan.
- **Buxgalteriya O'chirish Siyosati (Accounting Deletion Policy)**: Moliyaviy hisobotlar va to'lovlar tarixi butunligini ta'minlash maqsadida to'lov qilgan o'quvchilarni o'chirish qat'iy taqiqlanadi (HTTP 400 Bad Request).
- **Telegram Bot (`aiogram 3.x` + `HTTPX`)**: Vercel bulutida Serverless Webhook orqali kompyuteringiz o'chiq bo'lsa ham 24/7 onlayn ishlovchi admin boti.
- **Avtomatlashtirilgan Testlar**: 31 ta to'liq unit va integratsion testlar to'plami (`pytest`).

---

## 🌐 Jonli Havolalar (Vercel Production — 24/7 Onlayn)

- **Admin Dashboard (Vebsayt)**: [https://job-flax-psi.vercel.app/](https://job-flax-psi.vercel.app/) yoki [https://job-flax-psi.vercel.app/dashboard](https://job-flax-psi.vercel.app/dashboard)
- **Interaktiv API Hujjatlari (Swagger UI)**: [https://job-flax-psi.vercel.app/docs](https://job-flax-psi.vercel.app/docs)
- **ReDoc API Hujjatlari**: [https://job-flax-psi.vercel.app/redoc](https://job-flax-psi.vercel.app/redoc)
- **Tizim Sog'lomligi (Health Check)**: [https://job-flax-psi.vercel.app/health](https://job-flax-psi.vercel.app/health)
- **Telegram Bot**: [@ecomedev_bot](https://t.me/ecomedev_bot)
- **GitHub Ombori**: [https://github.com/Javohirbek070/ecomdev-payment-tracker](https://github.com/Javohirbek070/ecomdev-payment-tracker)

---

## 1. Loyihaning Asosiy Imkoniyatlari

### A. Admin Dashboard (Foydalanuvchi interfeysi)
1. **Boshqaruv Paneli (Dashboard)**:
   - Jami o'quvchilar soni (Faol talabalar).
   - Kutilayotgan oylik to'lov summasi (Belgilangan reja).
   - Tanlangan oyda yig'ilgan tushum (Fakt to'lovlar summasi).
   - Qoldiq qarz summasi va qarzdor o'quvchilar soni.
   - Oxirgi qabul qilingan to'lovlar ro'yxati (Talaba va guruh nomlari bilan).
   - Kalendar oy bo'yicha interaktiv filtr (`YYYY-MM`).
2. **O'quvchilar Boshqaruvi (Students)**:
   - F.I.Sh, telefon raqami yoki guruh bo'yicha tezkor qidiruv.
   - Yangi o'quvchi qo'shish formasi (Valitatsiya bilan: to'liq ism, telefon, guruh, ijobiy oylik tarif).
   - O'quvchi ma'lumotlarini tahrirlash (Edit).
   - O'quvchi profili va shaxsiy to'lovlar tarixi (Modal oyna).
   - Xavfsiz o'chirish: agar o'quvchining to'lov tarixi mavjud bo'lsa, buxgalteriya talablari sababli o'chirish avtomatik bloklanadi.
3. **To'lovlar Boshqaruvi (Payments)**:
   - To'lov qabul qilish formasi (Talabani tanlash, tarif summasining avtomatik to'ldirilishi, to'lov sanasini tanlash).
   - Barcha to'lov cheklari ro'yxati (O'quvchi, guruh, summa va sana).
4. **Qarzdorlar Tahlili (Debtors)**:
   - Tanlangan oy bo'yicha qarzdorlar ro'yxati (`YYYY-MM`).
   - "Qisman to'langan" va "To'lanmagan" holatlarining ajratib ko'rsatilishi.
   - Qarz formulasi: `qoldiq_qarz = oylik_tarif - to'langan_summa`.
   - Qarzdor talaba uchun bir tugma bilan to'lov qabul qilish amali.
5. **Moslashuvchan Dizayn (Responsive Layout)**:
   - Katta ekranlar (Desktop) uchun chap tomondagi qulay yon panel (Sidebar).
   - Mobil qurilmalar (Smartfonlar) uchun ixcham ochiluvchi menyu (Mobile drawer).

### B. REST API Backend
- **CRUD operatsiyalari**: `POST /students`, `GET /students`, `GET /students/{id}`, `PATCH /students/{id}`, `DELETE /students/{id}`.
- **To'lovlar operatsiyalari**: `POST /payments`, `GET /payments`, `GET /students/{id}/payments`.
- **Qarzdorlik tahlili**: `GET /debtors?month=YYYY-MM` (Noto'g'ri oy formati kiritilganda **HTTP 422** qaytaradi).
- **Statistika**: `GET /dashboard/summary?month=YYYY-MM` (Frontend uchun barcha moliyaviy ma'lumotlarni hisoblaydi).
- **CORS sozlamalari**: Istalgan mijozdan xavfsiz so'rovlarni qabul qilish uchun `CORSMiddleware` sozlangan.

### C. Telegram Bot (`aiogram 3.x` + `HTTPX`)
- **Doimiy 24/7 onlayn**: Vercel Serverless Webhook (`POST /webhook/telegram`) orqali kompyuteringiz o'chiq bo'lsa ham ishlaydi.
- **Ruxsatlar tizimi (RBAC)**: Moliyaviy amallarni (`/pay`) faqat tasdiqlangan adminlar bajara oladi.
- **Ruxsat berilgan adminlar**: `@The_javohirbek` (Telegram ID: `6752851778`) va `@code_debugger007`.
- **Buyruqlar**:
  - `/start` — Bot haqida ma'lumot va yo'riqnoma.
  - `/debt` — Joriy kalendar oy bo'yicha qarzdorlar ro'yxatini ko'rish.
  - `/pay <student_id> <summa>` — O'quvchi uchun to'lov qabul qilish (Masalan: `/pay 2 350000`).

---

## 2. Texnologiyalar Steki

| Qism | Texnologiya | Versiya / Tavsif |
| :--- | :--- | :--- |
| **Frontend** | React | 19.x (Zamonaviy komponentlar) |
| **Frontend** | TypeScript | 6.x (Xavfsiz va qat'iy tiplashtirish) |
| **Frontend** | Vite | 8.x (Yuqori tezlikdagi yig'uvchi) |
| **Frontend** | Tailwind CSS | v4 (Toza va moslashuvchan dizayn) |
| **Frontend** | Lucide Icons | Interfeys belgilari to'plami |
| **Backend** | Python | 3.11+ (Python 3.12 da sinovdan o'tgan) |
| **Backend** | FastAPI | 0.110+ (Yuqori tezlikdagi asinxron API) |
| **Backend** | Uvicorn | 0.28+ (ASGI veb-server) |
| **Ma'lumotlar bazasi** | SQLite | SQLAlchemy 2.x ORM orqali |
| **Validatsiya** | Pydantic v2 | 2.6+ & pydantic-settings |
| **Telegram Bot** | aiogram 3.x | 3.4+ & HTTPX 0.27+ |
| **Avtotestlar** | pytest | 8.0+ & pytest-asyncio |

---

## 3. Loyiha Arxitekturasi va Kataloglar Tuzilishi

```text
ecomdev-payment-tracker/
├── app/
│   ├── __init__.py           # Paket identifikatori
│   ├── config.py             # Muhit sozlamalari loaderi (Pydantic Settings)
│   ├── database.py           # Dvigatel, sessiya, SQLite pragma va Base
│   ├── models.py             # SQLAlchemy 2.0 ORM modellari (Student, Payment)
│   ├── schemas.py            # Pydantic v2 validation sxemalari (MoneyDecimal)
│   ├── crud.py               # Ma'lumotlar bazasi operatsiyalari va o'chirish siyosati
│   ├── exceptions.py         # Maxsus dasturiy xatoliklar (Exceptions)
│   ├── services/
│   │   ├── __init__.py
│   │   └── debtors.py        # Oylik qarzdorlikni aniq Decimal da hisoblash xizmati
│   ├── api/
│   │   ├── __init__.py
│   │   ├── students.py       # /students CRUD yo'nalishlari
│   │   ├── payments.py       # /payments va to'lovlar tarixi yo'nalishlari
│   │   ├── debtors.py        # /debtors?month=YYYY-MM yo'nalishi
│   │   └── dashboard.py      # /dashboard/summary tahliliy hisobot yo'nalishi
│   └── main.py               # FastAPI ilovasi, CORS, statik fayllar va /health
├── bot/
│   ├── __init__.py
│   └── main.py               # aiogram 3.x bot dispecheri va HTTPX mijozi
├── frontend/
│   ├── dist/                 # Ishlab chiqarish uchun yig'ilgan statik fayllar
│   ├── src/
│   │   ├── components/       # Header, Sidebar, StatCard, Modal, ConfirmModal
│   │   ├── views/            # DashboardView, StudentsView, PaymentsView, DebtorsView
│   │   ├── services/         # API mijozi (api.ts - dinamik nisbiy URL bilan)
│   │   ├── types/            # TypeScript interfeyslari (index.ts)
│   │   ├── utils/            # Valyuta va sana formatlovchi yordamchilar (format.ts)
│   │   ├── App.tsx           # Asosiy sahifa va navigatsiya
│   │   ├── main.tsx          # Ilova kirish nuqtasi
│   │   └── index.css         # Tailwind CSS uslublari
│   ├── .env.example          # Frontend muhit o'zgaruvchilari namunasi
│   ├── package.json          # Frontend paketlari ro'yxati
│   └── vite.config.ts        # Vite konfiguratsiyasi
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Alohida in-memory SQLite bazasi va TestClient
│   ├── test_students.py      # O'quvchilar CRUD va o'chirish siyosati testlari
│   ├── test_payments.py      # To'lovlarni yozish va olish testlari
│   ├── test_debtors.py       # Qarzdorlikni hisoblash va kalendar chegaralari testlari
│   ├── test_dashboard.py     # Dashboard statistikasi va statik fayllar testlari
│   └── test_bot.py           # Telegram bot buyruqlari va ruxsatlar testlari
├── .env.example              # Backend muhit o'zgaruvchilari namunasi
├── .gitignore                # Git e'tiborsiz qoldiradigan fayllar qoidalari
├── requirements.txt          # Python kutubxonalari ro'yxati
├── vercel.json               # Vercel serverless sozlamalari
├── main.py                   # Vercel ASGI kirish nuqtasi
├── run.py                    # Mahalliy server va botni birga yurgizuvchi skript
└── README.md                 # Loyiha hujjatlari (O'zbek tilida)
```

---

## 4. O'rnatish va Sozlash Yo'riqnomasi

### A. Windows 11 (PowerShell)

```powershell
# 1. Loyiha papkasiga o'ting
cd c:\Users\Lenovo\Desktop\job

# 2. Python virtual muhitini yarating va faollashtiring
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Python kutubxonalarini o'rnating
pip install -r requirements.txt

# 4. Muhit o'zgaruvchilarini nusxalang
Copy-Item .env.example .env

# 5. Frontend kutubxonalarini o'rnating va yig'ing (build)
cd frontend
npm install
npm run build
cd ..
```

### B. Linux / macOS (Bash)

```bash
# 1. Loyiha papkasiga o'ting
cd /path/to/project

# 2. Virtual muhitni yarating va faollashtiring
python3 -m venv .venv
source .venv/bin/activate

# 3. Kutubxonalarni o'rnating
pip install -r requirements.txt

# 4. Muhit o'zgaruvchilarini nusxalang
cp .env.example .env

# 5. Frontend kutubxonalarini o'rnating va yig'ing
cd frontend
npm install
npm run build
cd ..
```

---

## 5. Muhit O'zgaruvchilari (.env)

Loyiha ildizidagi `.env` faylida quyidagi parametrlar sozlanadi:

```env
# Ma'lumotlar bazasi
DATABASE_URL=sqlite:///./learning_center.db

# API Server konfiguratsiyasi
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=development

# Telegram Bot konfiguratsiyasi
API_BASE_URL=http://127.0.0.1:8000
TELEGRAM_BOT_TOKEN=8744717265:AAHEnHE7d73OOfp1fbT6ChEyMhG_wqo6wU4
TELEGRAM_ADMIN_IDS=6752851778
TELEGRAM_ADMIN_USERNAMES=code_debugger007,The_javohirbek
```

---

## 6. Loyihani Mahalliy Ishga Tushirish

### 1-usul: Hammasini Birgalikda Ishga Tushirish (Tavsiya etiladi)
Ushbu buyruq FastAPI serverini (ichki React Dashboard bilan) va Telegram botni bir vaqtda ishga tushiradi:
```powershell
.venv\Scripts\Activate.ps1
python run.py
```
Brauzer orqali oching:
- **Admin Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) yoki [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Swagger API**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2-usul: Frontendni Dasturchi Rejimida Ishlatish (HMR)
Frontend kodini o'zgartirganda darhol ko'rish uchun:
```powershell
cd frontend
npm run dev
```
Manzil: [http://localhost:5173](http://localhost:5173).

---

## 7. Avtomatlashtirilgan Testlar

Loyiha 31 ta alohida unit va integratsion testlar bilan to'liq qamrab olingan:
```powershell
.venv\Scripts\Activate.ps1
pytest -v
```

### Sinov Natijalari (100% PASS):
```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-8.4.2 -- .venv\Scripts\python.exe
collected 31 items

tests/test_bot.py::test_bot_authorization PASSED                         [  3%]
tests/test_bot.py::test_bot_start_command PASSED                         [  6%]
tests/test_bot.py::test_bot_pay_unauthorized PASSED                      [  9%]
tests/test_bot.py::test_bot_pay_invalid_arguments PASSED                 [ 12%]
tests/test_bot.py::test_bot_pay_and_debt_with_httpx PASSED               [ 16%]
tests/test_bot.py::test_bot_handles_network_error PASSED                 [ 19%]
tests/test_bot.py::test_telegram_webhook_endpoint PASSED                 [ 22%]
tests/test_dashboard.py::test_list_all_payments_with_student_name PASSED [ 25%]
tests/test_dashboard.py::test_dashboard_summary_calculations PASSED      [ 29%]
tests/test_dashboard.py::test_dashboard_summary_invalid_month PASSED     [ 32%]
tests/test_dashboard.py::test_frontend_serving_endpoints PASSED          [ 35%]
tests/test_debtors.py::test_debt_after_partial_payment PASSED            [ 38%]
tests/test_debtors.py::test_exclude_fully_paid_students PASSED           [ 41%]
tests/test_debtors.py::test_exclude_overpaid_students PASSED             [ 45%]
tests/test_debtors.py::test_aggregate_multiple_payments_in_one_month PASSED [ 48%]
tests/test_debtors.py::test_ignore_payments_outside_requested_month PASSED [ 51%]
tests/test_debtors.py::test_handle_month_with_no_payments PASSED         [ 54%]
tests/test_debtors.py::test_reject_invalid_month_formats PASSED          [ 58%]
tests/test_payments.py::test_record_payment_success PASSED               [ 61%]
tests/test_payments.py::test_reject_payment_for_nonexistent_student PASSED [ 64%]
tests/test_payments.py::test_reject_invalid_payment_amounts PASSED       [ 67%]
tests/test_payments.py::test_list_student_payment_history PASSED         [ 70%]
tests/test_payments.py::test_list_payments_nonexistent_student PASSED    [ 74%]
tests/test_students.py::test_create_student_success PASSED               [ 77%]
tests/test_students.py::test_list_and_retrieve_students PASSED           [ 80%]
tests/test_students.py::test_update_student PASSED                       [ 83%]
tests/test_students.py::test_handle_nonexistent_student PASSED           [ 87%]
tests/test_students.py::test_reject_invalid_monthly_fees PASSED          [ 90%]
tests/test_students.py::test_reject_empty_required_fields PASSED         [ 93%]
tests/test_students.py::test_delete_student_without_payments PASSED      [ 96%]
tests/test_students.py::test_delete_student_with_payment_history_blocked PASSED [100%]

======================== 31 passed in 2.52s ========================
```

---

## 8. REST API Ma'lumotnomasi

| Metod | Endpoint | Tavsif |
| :--- | :--- | :--- |
| `GET` | `/` | Asosiy sahifa: brauzerlar uchun Dashboard, dasturlar uchun JSON qaytaradi |
| `GET` | `/health` | Server sog'lomligini monitoring qilish tekshiruvi |
| `GET` | `/dashboard/summary?month=YYYY-MM` | Dashboard ko'rsatkichlari (talabalar soni, reja, tushum, qarz) |
| `GET` | `/students` | Barcha o'quvchilar ro'yxatini olish |
| `POST` | `/students` | Yangi o'quvchini ro'yxatga olish |
| `GET` | `/students/{student_id}` | Bitta o'quvchi ma'lumotlarini olish |
| `PATCH` | `/students/{student_id}` | O'quvchi ma'lumotlarini qisman yangilash |
| `DELETE` | `/students/{student_id}` | O'quvchini o'chirish (to'lov tarixi bo'lsa **HTTP 400** qaytaradi) |
| `POST` | `/payments` | Yangi to'lovni qayd qilish |
| `GET` | `/payments?skip=0&limit=50` | Oxirgi to'lovlar ro'yxatini talaba ismi bilan olish |
| `GET` | `/students/{student_id}/payments` | Muayyan o'quvchining to'lovlar tarixini olish |
| `GET` | `/debtors?month=YYYY-MM` | Berilgan oy bo'yicha qarzdorlar ro'yxatini olish |
| `POST` | `/webhook/telegram` | Telegram boti uchun serverless webhook qabul qiluvchisi |

---

## 9. AI Foydalanish Hisoboti (AI Usage Report)

Ishga qabul qilish talablariga muvofiq:
- **Arxitektura va Loyihalash**: Antigravity AI pair programming yordamchisi tizim arxitekturasini loyihalash, `Decimal` orqali moliya hisobini yuritish, Pydantic v2 sxemalari, FastAPI endpointlari va React 19 boshqaruv panelini qurishda qo'llanildi.
- **Kod Yozish**: Backend CRUD operatsiyalari, aiogram 3.x Telegram webhook dispecheri, moslashuvchan o'zbekcha UI komponentlari va 31 ta pytest testlari yozildi.
- **Tekshiruv va Testlash**: Barcha kodlar mahalliy kompyuterda va Vercel bulutida sinovdan o'tkazildi. Testlarning 100% muvaffaqiyatli o'tishi va Vercel serverless webhooki orqali bot va saytning 24/7 ishlashi amalda to'liq tasdiqlandi.
