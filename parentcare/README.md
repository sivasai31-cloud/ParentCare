# ParentCare — Family Healthcare Coordination Platform

ParentCare is a full-stack healthcare coordination platform designed for individuals who live away from their aging parents. It streamlines medication schedules, doctor appointments, medical reports vault, emergency contacts, and one-tap SOS dialing.

---

## Key Features

- **Care Dashboard**: Real-time overview of daily medication schedules, upcoming appointments, emergency contacts, and medical alerts.
- **Parent Management**: Comprehensive medical profile tracking including blood groups, known allergies, emergency notes, and contact details.
- **Medication Manager**: Course tracking, dosage frequency, instructions, and status (active, completed, stopped).
- **Doctor Appointments**: Consultation scheduling, clinic location mapping, status tracking, and doctor notes.
- **Medical Records Vault**: Secure uploads and downloads for laboratory tests, prescriptions, radiology scans, and discharge summaries.
- **Health Monitoring**: User-entered blood pressure, glucose, temperature, weight, and heart-rate records with history and simple trends.
- **Emergency SOS & 1-Tap Calling**: Priority-based directory (Primary, Secondary, Doctor) with direct `tel:` dialing.
- **Notification Center**: Persistent account notifications. Scheduled dose and appointment reminders are not currently delivered.
- **Role-Based Access Control & Admin Portal**: Multi-role security (`USER`, `ADMIN`, `PARENT`) and account management.

---

## Tech Stack

- **Frontend**: React 19, Vite, TypeScript, Lucide React, Modern CSS (Responsive Design, CSS Custom Properties).
- **Backend**: FastAPI, SQLAlchemy ORM, Pydantic V2, PyJWT, Bcrypt, Python-Multipart.
- **Database**: SQLite (local development / testing) / PostgreSQL (production ready).

---

## Project Structure

```
parentcare/
├── backend/
│   ├── app/
│   │   ├── api/             # REST API routers (auth, parents, medicines, appointments, reports, etc.)
│   │   ├── core/            # Config, security, database session setup
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic V2 schemas
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # Pytest automated test suites
│   ├── requirements.txt     # Python dependencies
│   └── seed_demo.py         # Optional demo data seeder
└── frontend/
    ├── src/
    │   ├── api/             # Centralized API client & endpoint modules
    │   ├── components/      # Reusable UI components (Sidebar, Navbar, Modal, Layout, etc.)
    │   ├── context/         # AuthContext & state management
    │   ├── pages/           # Pages (Dashboard, Parents, Medicines, Appointments, Reports, Emergency, Admin, Profile)
    │   ├── types/           # TypeScript interfaces
    │   ├── App.tsx          # Router configuration
    │   └── index.css        # Modern design system & styles
    ├── package.json
    └── vite.config.ts
```

---

## Environment Variables

### Backend (`backend/.env` or environment):
```env
PROJECT_NAME="ParentCare"
APP_ENV=development
SECRET_KEY="generate-a-unique-secret-and-keep-it-private"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DATABASE_URL="sqlite:///./parentcare.db"
UPLOAD_DIR="./uploads"
FRONTEND_URL="http://localhost:5173"
SEED_DEMO_USERS=false
```

### Frontend (`frontend/.env`):
```env
# Development uses Vite's /api proxy by default.
# Production must point to the deployed backend:
# VITE_API_URL="https://your-backend.example.com/api"
```

---

## Getting Started Locally

### 1. Backend Setup
```bash
Set-Location parentcare\backend
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# Optional: add fictional demo records only to a local development database.
python seed_demo.py

# Start the API:
uvicorn app.main:app --reload --port 8000
```
API documentation: `http://127.0.0.1:8000/api/docs`
Database health check: `http://127.0.0.1:8000/healthz`

### 2. Frontend Setup
```bash
Set-Location parentcare\frontend
npm install
npm run dev
```
Frontend development server: `http://127.0.0.1:5173`

---

The Windows convenience scripts at the repository root start both services in separate terminals. The backend script intentionally selects local SQLite for local use.

## Security and privacy notes

- Configure a unique `SECRET_KEY` and a production `DATABASE_URL` before deploying. Production startup rejects SQLite and refuses to start without an explicit signing key.
- Demo users are no longer created automatically. `SEED_DEMO_USERS=true` is only permitted in development. The optional seeder creates fictional data and must never be run against production.
- If an earlier run created the known demo/admin accounts in a real database, remove or disable them there before deployment; disabling automatic seeding does not remove existing rows.
- Medical records are stored in the configured upload directory and served only through authenticated API routes. Back up that directory securely alongside the database.
- Health readings are manually entered, are not verified or diagnostic, and should be interpreted with a healthcare professional. No medical alerts or automatic emergency dispatch are provided.
- Password reset email delivery is not configured. Development returns a short-lived reset token directly; production does not expose a token and directs users to an administrator.
- Account access currently belongs to the account that created a parent profile (plus administrators). Shared caregiver invitations and consent-based family access are not implemented.
- The current interface is English-only. Telugu translations and large-text/high-contrast preferences are not implemented.

## Deployment

The frontend project root is `parentcare/frontend`; build with `npm run build` and publish `dist`. Configure `VITE_API_URL` to the deployed backend URL ending in `/api`, and configure the backend `FRONTEND_URL` to the exact deployed frontend origin.

The backend project root is `parentcare/backend`; install `requirements.txt` and start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Configure `APP_ENV=production`, `SECRET_KEY`, `DATABASE_URL`, `UPLOAD_DIR` (persistent private storage), and `FRONTEND_URL`. The `/healthz` endpoint checks database connectivity.

No hosted deployment URL or external account has been configured. Database tables are created with SQLAlchemy `create_all`; this repository does not yet include a versioned migration system, so review schema changes and take backups before production updates.

## Tests

```powershell
Set-Location parentcare\backend
python -m pytest -q

Set-Location ..\frontend
npm run build
```

---

## Healthcare Disclaimer

> **Important Notice:** ParentCare is a healthcare coordination and record tracking tool. It does **not** replace professional medical advice, diagnosis, or national emergency services (e.g., 911, 112, 108). In case of a medical emergency, immediately contact your local emergency response services.
