"""Import all models here so Alembic & SQLAlchemy metadata can discover them."""

from app.models.division import Division
from app.models.district import District
from app.models.user import User
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.request_match import RequestMatch
from app.models.donation import Donation
from app.models.hospital import Hospital
from app.models.hospital_inventory import HospitalInventory
from app.models.notification import Notification
from app.models.audit_log import AuditLog
