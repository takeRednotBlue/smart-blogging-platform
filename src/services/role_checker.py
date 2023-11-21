import logging

from fastapi import Depends, HTTPException, status

from src.database.models.users import User
from src.services.auth import auth_service

logger = logging.getLogger("BaseLogger")


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(auth_service.get_current_user)):
        if user.roles not in self.allowed_roles:
            logger.info(
                f"User {user.email} with role {user.roles} is not in allowed roles {self.allowed_roles}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
