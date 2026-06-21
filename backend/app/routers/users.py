from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_profile(payload: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # TODO: User.updateProfile()
    raise NotImplementedError


@router.delete("/me", status_code=204)
def deactivate_account(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # TODO: User.deactivate() — soft delete via is_active flag
    raise NotImplementedError
