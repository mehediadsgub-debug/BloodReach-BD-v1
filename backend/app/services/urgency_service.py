"""Urgency queue and escalation logic for blood requests."""

from sqlalchemy.orm import Session


def enqueue_request(request, db: Session):
    # TODO: insert into priority queue ordered by urgency_level (CRITICAL first)
    raise NotImplementedError


def escalate_unmatched_critical_requests(db: Session):
    # TODO: find CRITICAL requests with status=PENDING for >30 minutes,
    # broaden the search radius (division-wide) and re-trigger matching/notifications.
    raise NotImplementedError
