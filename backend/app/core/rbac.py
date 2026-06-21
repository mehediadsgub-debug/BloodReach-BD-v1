from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.utils.enums import Role


def require_role(*allowed_roles: Role):
    """Dependency factory for role-based route guards.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(Role.SUPERADMIN))])
    """

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker
