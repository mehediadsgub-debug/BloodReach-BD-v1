"""
BloodReach BD — Urgency Escalation Service
Background job that checks for critical/urgent pending requests and sends alerts.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import BloodRequest, RequestMatch, MatchStatus, User, UserRole, Donor, District
from app.services.notification_service import NotificationService
from app.core.config import settings


class EscalationService:
    """Handles urgency escalation for critical/pending blood requests"""

    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def check_and_escalate_critical_requests(self) -> dict:
        """
        Check for critical/high urgency requests that are still pending
        and escalate by notifying more donors.
        """
        results = {
            "checked": 0,
            "escalated": 0,
            "sms_sent": 0,
            "errors": []
        }

        # Find pending critical and high urgency requests older than threshold
        critical_threshold = datetime.utcnow() - timedelta(minutes=30)  # 30 min for critical
        high_threshold = datetime.utcnow() - timedelta(hours=2)  # 2 hours for high

        requests = self.db.query(BloodRequest).filter(
            and_(
                BloodRequest.status.in_(["OPEN", "IN_PROGRESS"]),
                or_(
                    and_(
                        BloodRequest.urgency_level == "CRITICAL",
                        BloodRequest.created_at < critical_threshold
                    ),
                    and_(
                        BloodRequest.urgency_level == "HIGH",
                        BloodRequest.created_at < high_threshold
                    )
                )
            )
        ).all()

        results["checked"] = len(requests)

        for request in requests:
            try:
                escalated = self._escalate_request(request)
                if escalated:
                    results["escalated"] += 1
                    results["sms_sent"] += escalated.get("sms_count", 0)
            except Exception as e:
                results["errors"].append(f"Request {request.request_id}: {str(e)}")

        return results

    def _escalate_request(self, request: BloodRequest) -> Optional[dict]:
        """Escalate a single request by finding more donors and sending alerts"""
        from app.services.matching_service import MatchingEngine

        matching_engine = MatchingEngine(self.db)

        # Get already matched donors to avoid duplicate notifications
        matched_donor_ids = [
            m.donor_id for m in request.matches
            if m.status in [MatchStatus.PENDING, MatchStatus.ACCEPTED]
        ]

        # Find more donors with wider search radius
        requester_district_id = request.district_id
        requester_division_id = None

        if requester_district_id:
            district = self.db.query(District).filter(District.district_id == requester_district_id).first()
            if district:
                requester_division_id = district.division_id

        # Search for more donors (increase limit for escalation)
        donors = matching_engine.find_matching_donors(
            blood_group=request.blood_group,
            requester_district_id=requester_district_id,
            requester_division_id=requester_division_id,
            urgency_level=request.urgency_level,
            limit=20  # Wider search for escalation
        )

        # Filter out already matched donors
        new_donors = [d for d in donors if d.donor_id not in matched_donor_ids]

        if not new_donors:
            return {"sms_count": 0}

        # Create matches for new donors
        new_matches = matching_engine.create_matches(request, [d.donor_id for d in new_donors])

        # Send notifications to new donors
        sms_count = 0
        for donor in new_donors:
            user = donor.user
            # System notification
            self.notification_service.notify_donor_match(user.user_id, request, donor.donor_id)

            # SMS for critical urgency
            if request.urgency_level == "CRITICAL" and user.phone:
                sent = self.notification_service.notify_donor_match_sms(user.phone, request)
                if sent:
                    sms_count += 1

        return {"sms_count": sms_count, "new_matches": len(new_matches)}

    def send_escalation_alert_to_admins(self, request: BloodRequest) -> None:
        """Send escalation alert to hospital admins in the area"""
        if not request.district_id:
            return

        # Find hospital admins in the same district/division
        district = self.db.query(District).filter(District.district_id == request.district_id).first()
        if not district:
            return

        admins = self.db.query(User).filter(
            and_(
                User.role == UserRole.HOSPITAL_ADMIN,
                User.is_active == True,
                or_(
                    User.district_id == request.district_id,
                    # Also check hospital's district
                    User.user_id.in_(
                        self.db.query(User.user_id).join(User.hospital_admin).filter(
                            User.hospital_admin.has(district_id=request.district_id)
                        )
                    )
                )
            )
        ).all()

        for admin in admins:
            title = f"Escalation: {request.urgency_level} Request for {request.blood_group}"
            message = (
                f"Request {request.request_id} for {request.blood_group} "
                f"({request.units_needed} units) in {district.name} has been pending "
                f"and requires attention."
            )
            self.notification_service.send_system_notification(admin.user_id, title, message, request.request_id)


def run_escalation_job(db: Session) -> dict:
    """Entry point for APScheduler job"""
    service = EscalationService(db)
    return service.check_and_escalate_critical_requests()