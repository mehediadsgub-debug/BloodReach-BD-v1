import enum


class Role(str, enum.Enum):
    DONOR = "DONOR"
    SEEKER = "SEEKER"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    SUPERADMIN = "SUPERADMIN"


class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class MatchStatus(str, enum.Enum):
    NOTIFIED = "NOTIFIED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    FULFILLED = "FULFILLED"


class NotificationType(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    SYSTEM = "SYSTEM"
