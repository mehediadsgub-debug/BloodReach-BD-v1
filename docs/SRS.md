# Software Requirements Specification — Blood Reach BD

> Week 1 deliverable per project roadmap. Expand each section below.

## 1. Introduction
- Purpose, scope, intended audience

## 2. Functional Requirements
- User registration & authentication (JWT, bcrypt)
- Donor availability & profile management
- Blood request creation, tracking, fulfillment
- Location-based donor matching (district/division)
- Urgency prioritisation & escalation
- Hospital inventory management & low-stock alerts
- Notifications (email/SMS)
- Role-based access control
- Analytics dashboard (Superadmin)

## 3. Non-Functional Requirements
- API response time < 300ms (p95)
- Test coverage ≥ 80%
- Notification delivery rate ≥ 95%
- Security: short-lived JWTs, HTTPS, bcrypt hashing

## 4. Use Cases
- TODO: detail each user role's primary use cases

## 5. Constraints
- 10-week academic timeline
- Stack: FastAPI, PostgreSQL, vanilla HTML/CSS/JS
