# 🩸 Blood Reach BD

**A Real-Time Blood Availability & Donor Matching Platform**  
Covering all 64 Districts & 8 Divisions of Bangladesh

> "Connecting donors, seekers, and hospitals — one drop at a time."

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)]([https://blood-reach-bd.vercel.app](https://blood-reach-bd-v1.vercel.app/))
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/mehediadsgub-debug/BloodReach-BD-v1)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org)

🌐 **Live Demo Website:** [https://blood-reach-bd.vercel.app](https://blood-reach-bd.vercel.app)

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [User Roles](#user-roles)
- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Weekly Roadmap](#weekly-roadmap)
- [Risks & Mitigations](#risks--mitigations)
- [Success Metrics](#success-metrics)
- [Author](#author)
- [License](#license)

---

## 📖 About the Project

**Blood Reach BD** is an enterprise full-stack web platform designed to solve critical blood availability challenges across Bangladesh. The system connects blood donors, seekers, and hospital administrators in real time through intelligent location-based matching, urgency prioritisation, and automated notifications.

**Mission:** To eliminate preventable deaths caused by blood unavailability in Bangladesh by providing a reliable, real-time digital bridge between donors and recipients — empowering hospitals and individuals alike with transparent, data-driven tools.

## ❗ Problem Statement

- Patients in emergency situations cannot find matching donors quickly enough.
- Hospital blood banks lack real-time inventory visibility across the network.
- Existing solutions are fragmented, offline, or geographically limited.
- No centralised platform connects all 64 districts of Bangladesh under one unified system.

## ✨ Key Features

- 🩸 Instant donor–seeker matching filtered by blood group and district
- 🚨 Real-time urgency queue for critical requests (with auto-escalation)
- 🏥 Hospital inventory management with low-stock alerts
- 👥 Role-based dashboards for four user types (Donor, Seeker, Hospital Admin, Superadmin)
- 📊 Analytics for national blood supply monitoring
- 📍 Location-based matching across all 64 districts & 8 divisions
- 🔔 Automated WebSocket, SMS, and email notifications
- 🗺️ Public interactive 64-district live map for guests without login requirement

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy |
| **Database** | PostgreSQL 15+ / SQLite Fallback |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Leaflet.js |
| **Deployment** | Vercel Serverless Python (`@vercel/python`) & Static Hosting |
| **Authentication** | JWT, bcrypt (4.0.1) |
| **Testing** | pytest (30/30 automated tests passing) |
| **Version Control** | Git, GitHub |

## 👤 User Roles

| Badge | Role | Responsibilities |
|---|---|---|
| 🟥 `DONOR` | Donor | Register availability, update blood group & location, respond to requests, view donation history |
| 🟦 `SEEKER` | Seeker | Post blood requests, browse nearby donors, mark requests as fulfilled |
| 🟩 `HOSPITAL_ADMIN` | Hospital Admin | Manage hospital blood inventory, approve/reject requests, view stock reports |
| 🟨 `SUPERADMIN` | Superadmin | Full platform access: user management, analytics, system settings, audit logs |

## 🏗 System Architecture

A three-tier web application:

```
Frontend (HTML/CSS/JS/Leaflet)  ⇄  Serverless API (FastAPI)  ⇄  Database (PostgreSQL / SQLite)
```

## 🗄 Database Schema

**Core Entities:**

| Table | Primary Key | Description |
|---|---|---|
| `users` | `user_id` (UUID) | All registered accounts (donor, seeker, hospital admin, superadmin) |
| `donors` | `donor_id` (UUID) | Donor-specific profile (1:1 with `users`) |
| `blood_requests` | `request_id` (UUID) | Requests posted by seekers |
| `request_matches` | `match_id` (UUID) | Junction table linking donors to requests |
| `donations` | `donation_id` (UUID) | Created automatically when a match is fulfilled |
| `hospitals` | `hospital_id` (UUID) | Hospital profiles |
| `hospital_inventory` | `inv_id` (UUID) | Blood stock per hospital, per blood group |
| `districts` | `district_id` (INT) | 64 districts of Bangladesh |
| `divisions` | `division_id` (INT) | 8 divisions of Bangladesh |
| `notifications` | `notif_id` (UUID) | Email/SMS/system alerts |
| `audit_logs` | `log_id` (UUID) | Action history for sensitive operations |

## 📁 Project Structure

```
BloodReach-BD-v1/
├── api/
│   └── index.py               # Vercel Serverless FastAPI handler
├── backend/
│   ├── app/
│   │   ├── core/              # Database, security, config
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # FastAPI route handlers
│   │   ├── schemas/           # Pydantic validation schemas
│   │   └── services/          # Matching engine & business logic
│   ├── tests/                 # 30 Automated pytest tests
│   ├── main.py                # Local FastAPI server entrypoint
│   └── setup_db.py            # Database initializer & 64-district seeder
├── frontend/
│   ├── assets/                # CSS, JS (cloud-sync.js, login.js, register.js)
│   ├── index.html             # Public interactive map & Bangladesh blood stream
│   ├── login.html             # Authentication portal
│   ├── register.html          # Registration portal (8 divisions & 64 districts)
│   ├── dashboard-donor.html   # Donor dashboard & 100km radar map
│   ├── dashboard-seeker.html  # Seeker dashboard & nearby donors map
│   ├── dashboard-admin.html   # Superadmin moderation & analytics
│   └── dashboard-hospital.html# Hospital inventory management
├── requirements.txt           # Python dependencies for Vercel & local setup
└── vercel.json                # Vercel Serverless & Static routing configuration
```

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Git

### Backend Setup

```bash
git clone https://github.com/<your-username>/blood-reach-bd.git
cd blood-reach-bd/backend

python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # then fill in DATABASE_URL, JWT_SECRET, etc.

alembic upgrade head              # run DB migrations
python -m app.utils.seed_districts   # seed 64 districts & 7 divisions

uvicorn app.main:app --reload
```

API will be live at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd ../frontend
# Serve with any static server, e.g.:
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.

## 📚 API Documentation

Auto-generated via FastAPI's built-in Swagger UI:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

```bash
cd backend
pytest --cov=app tests/
```

Target: **≥80% test coverage** on backend, zero P0 bugs at submission.

## 🗺 Weekly Roadmap

| Week | Phase | Focus |
|---|---|---|
| 1 | Planning | SRS, DFD, ERD, GitHub setup |
| 2–3 | Backend I | Project skeleton, DB design, auth endpoints |
| 4–5 | Backend II | Donor, requests, location-based matching |
| 6 | Backend III | Notifications, urgency engine, RBAC |
| 7 | Frontend | HTML templates, CSS design system, JS interactions |
| 8 | Integration | Frontend ↔ API wiring, testing flows |
| 9 | Testing | Unit/integration tests, bug fixes |
| 10 | Deployment | Final docs, demo, GitHub release |

## ⚠ Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Scope creep | High | Module freeze after Week 2 |
| Notification delivery failures | Medium | Retry queue + fallback SMS |
| DB performance at scale | Medium | Indexing on `district_id`, `blood_group`, `urgency_level` |
| Auth token leakage | High | Short-lived JWTs (15 min) + refresh rotation + HTTPS |
| Time overrun | Medium | Weekly milestone checkpoints, MVP scoped to Weeks 1–6 |

## ✅ Success Metrics

- All 10 modules functional end-to-end
- API response time < 300ms (p95)
- Test coverage ≥ 80% on backend
- Zero P0 (critical) bugs at submission
- All 4 role dashboards fully operational
- District data for all 64 districts seeded
- Notification delivery rate ≥ 95%
- Live deployment accessible via public URL

## 👨‍🎓 Author

| Field | Detail |
|---|---|
| **Name** | Md. Mehedi Hasan |
| **Student ID** | 251035039 |
| **Program** | B.Sc. in AI and Data Science |
| **Course** | DBMS and SWE |
| **Supervisor** | Rakib Abdullah |
| **Semester** | Summer 2026 |

## 📄 License

This project is developed for **academic purposes** as part of the DBMS and SWE coursework. All rights reserved by the author unless otherwise specified.

---

<p align="center">Made with ❤️ for Bangladesh — Blood Reach BD</p>
