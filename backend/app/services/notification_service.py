"""Email/SMS notification dispatch."""


def send_email(to: str, subject: str, body: str):
    # TODO: integrate smtplib or Mailgun API
    raise NotImplementedError


def send_sms(to: str, message: str):
    # TODO: integrate SMS gateway (e.g. bKash API as fallback per roadmap risk mitigation)
    raise NotImplementedError


def notify_match_created(match, db):
    raise NotImplementedError
