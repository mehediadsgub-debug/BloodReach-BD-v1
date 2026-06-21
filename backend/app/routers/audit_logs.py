from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db

router = APIRouter()


@router.get("/")
def get_logs(action: str | None = None, entity_type: str | None = None, db: Session = Depends(get_db)):
    # TODO: AuditLog.getLogs(filters)
    raise NotImplementedError
