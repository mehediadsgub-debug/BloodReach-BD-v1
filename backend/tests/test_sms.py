"""
BloodReach BD — SMS Gateway Service Tests
"""

import pytest
from app.services.sms_service import MockSMSProvider, BDSMSGatewayProvider
from app.services.notification_service import NotificationService
from app.models import BloodRequest, UrgencyLevel, RequestStatus


def test_mock_sms_provider_dispatch():
    provider = MockSMSProvider()
    success = provider.send_sms("01711223344", "Urgent blood needed: O+ at Dhaka Medical College")
    assert success is True
    assert len(provider.sent_messages) == 1
    assert provider.sent_messages[0]["to"] == "01711223344"
    assert "O+" in provider.sent_messages[0]["message"]


def test_notification_service_sms_trigger(db_session, test_donor):
    service = NotificationService(db_session)
    test_request = BloodRequest(
        blood_group="B+",
        units_needed=2,
        urgency_level=UrgencyLevel.CRITICAL,
        status=RequestStatus.OPEN
    )

    # Trigger SMS to donor
    sent = service.notify_donor_match_sms(test_donor.phone, test_request)
    assert sent is True
