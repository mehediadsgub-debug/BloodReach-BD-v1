from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth,
    users,
    donors,
    blood_requests,
    matching,
    donations,
    hospitals,
    hospital_inventory,
    locations,
    notifications,
    analytics,
    audit_logs,
)

app = FastAPI(
    title="Blood Reach BD API",
    description="Real-Time Blood Availability & Donor Matching Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(donors.router, prefix="/donors", tags=["Donors"])
app.include_router(blood_requests.router, prefix="/blood-requests", tags=["Blood Requests"])
app.include_router(matching.router, prefix="/matching", tags=["Matching"])
app.include_router(donations.router, prefix="/donations", tags=["Donations"])
app.include_router(hospitals.router, prefix="/hospitals", tags=["Hospitals"])
app.include_router(hospital_inventory.router, prefix="/hospital-inventory", tags=["Hospital Inventory"])
app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])


@app.get("/")
def root():
    return {"message": "Blood Reach BD API is running."}
