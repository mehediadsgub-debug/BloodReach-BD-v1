"""
BloodReach BD — SMS Gateway Service
Provides SMS alerts for critical and emergency donor matching.
Supports Mock provider (for dev/tests) and production BD Gateway (SSL Wireless / Greenweb / generic HTTP API).
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BaseSMSProvider(ABC):
    """Abstract SMS Gateway Interface"""

    @abstractmethod
    def send_sms(self, recipient_phone: str, message: str) -> bool:
        """Send an SMS message to a single phone number. Returns True if successfully queued/sent."""
        pass


class MockSMSProvider(BaseSMSProvider):
    """Mock SMS provider for local development, demo, and automated tests"""

    def __init__(self):
        self.sent_messages = []

    def send_sms(self, recipient_phone: str, message: str) -> bool:
        cleaned_phone = recipient_phone.strip()
        logger.info(f"[MOCK SMS] >>> To: {cleaned_phone} | Message: {message}")
        self.sent_messages.append({
            "to": cleaned_phone,
            "message": message
        })
        return True


class BDSMSGatewayProvider(BaseSMSProvider):
    """
    Production-ready SMS Gateway Provider for Bangladesh
    Configured via environment variables:
      - SMS_GATEWAY_URL
      - SMS_API_KEY
      - SMS_SENDER_ID
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, sender_id: Optional[str] = None):
        self.api_url = api_url or os.getenv("SMS_GATEWAY_URL", "")
        self.api_key = api_key or os.getenv("SMS_API_KEY", "")
        self.sender_id = sender_id or os.getenv("SMS_SENDER_ID", "BloodReachBD")

    def send_sms(self, recipient_phone: str, message: str) -> bool:
        if not self.api_url or not self.api_key:
            # Fallback to mock logging if API keys are not supplied in .env
            logger.warning("SMS Gateway credentials missing in .env. Logging SMS in mock mode.")
            logger.info(f"[SMS DISPATCH] To: {recipient_phone} | Message: {message}")
            return True

        import httpx
        try:
            payload = {
                "api_key": self.api_key,
                "sender_id": self.sender_id,
                "recipient": recipient_phone,
                "message": message,
            }
            response = httpx.post(self.api_url, json=payload, timeout=5.0)
            if response.status_code in [200, 201]:
                logger.info(f"SMS dispatched to {recipient_phone} via gateway successfully.")
                return True
            else:
                logger.error(f"SMS Gateway error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"SMS transmission failed: {e}")
            return False


def get_sms_provider() -> BaseSMSProvider:
    """Factory to get configured SMS provider"""
    provider_type = os.getenv("SMS_PROVIDER", "MOCK").upper()
    if provider_type == "LIVE" or os.getenv("SMS_GATEWAY_URL"):
        return BDSMSGatewayProvider()
    return MockSMSProvider()


# Global default provider
default_sms_provider = get_sms_provider()
