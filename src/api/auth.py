from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_async_db
from src.repository import users as repository_users
from src.schemas.users import RequestEmail, TokenModel, UserModel, UserResponse
from src.services.auth import auth_service
from src.services.email import send_email

RequestLimiter = Depends(RateLimiter(times=10, seconds=60))
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncDBSession,
):
    """# Signup

    ### Description
    This endpoint is used to create a new user account. It takes in the user details as input and returns the created user object along with a success message. If the email provided already exists in the database, it will raise a conflict exception.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: Admin, Moderator, User.
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - None

    ### Returns
    - `UserResponse`: The created user object along with a success message.

    ### Raises
    - `HTTPException(status_code=409)`: Raised if the email provided already exists in the database.

    ### Example
    - Create a new user: [POST] `/signup`"""
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists.",
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.post("/login", response_model=TokenModel)
async def login(
    db: AsyncDBSession, body: OAuth2PasswordRequestForm = Depends()
):
    """# Login

    ### Description
    This endpoint is used to authenticate users and generate access and refresh tokens. The user must provide their email and password in the request body. If the email is invalid, not confirmed, or the password is incorrect, the endpoint will return an HTTP 401 Unauthorized error. If the authentication is successful, the endpoint will return an access token, a refresh token, and the token type.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: Admin, Moderator, User.
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - 10 requests per 60 seconds.

    ### Query Parameters
    None.

    ### Returns
    - `TokenModel`: A model containing the access token, refresh token, and token type.

    ### Raises
    - `HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)`: If the email is invalid, not confirmed, or the password is incorrect.

    ### Example
    - Authenticate user: [POST] `/login`"""
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email."
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed.",
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
        )
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    db: AsyncDBSession,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """# Refresh Token

    ### Description
    This endpoint is used to refresh the access token and obtain a new access token and refresh token pair. The refresh token is provided in the request header for authentication. If the refresh token is valid, a new access token and refresh token pair is generated and returned in the response.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    None.

    ### Returns
    - `TokenModel`: A JSON object containing the new access token, refresh token, and token type.

    ### Raises
    - `HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)`: Raised if the refresh token is invalid.

    ### Example
    - Refresh Token: [GET] `/refresh_token`"""
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncDBSession):
    """# Confirmed Email

    ### Description
    This endpoint is used to confirm a user's email address using a verification token.

    ### Authorization
    - This endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - Access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `token` (**str**, required): The verification token.

    ### Returns
    - `dict`: A dictionary containing a message indicating the status of the email confirmation.

    ### Raises
    - `HTTPException(status_code=status.HTTP_400_BAD_REQUEST)`: Raised if there is an error during the verification process.

    ### Example
    - Confirm email: [GET] `/confirmed_email/{token}`"""
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error.",
        )
    if user.confirmed:
        return {"massage": "Your email is already confirmed."}
    await repository_users.confirmed_email(email, db)
    return {"massage": "Your email has been confirmed."}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncDBSession,
):
    """# Request Email

    ### Description
    This endpoint is used to request email confirmation for a user. If the user's email is already confirmed, a message will be returned indicating that. Otherwise, an email will be sent to the user's email address for confirmation.

    ### Authorization
    - Access to this endpoint requires users to be authenticated.
    - Allowed roles: "Admin", "Moderator", "User".
    - The access JWT token should be passed in the request header for authentication.

    ### Request limit
    - Maximum of 10 requests per 60 seconds.

    ### Query Parameters
    - `body` (**RequestEmail**, required): The request body containing the user's email.
    - `background_tasks` (**BackgroundTasks**, required): Background tasks for sending the confirmation email.
    - `request` (**Request**, required): The request object.
    - `db` (**AsyncDBSession**, required): The database session.

    ### Returns
    - `dict`: A dictionary containing a message indicating the status of the email confirmation request.

    ### Raises
    - `HTTPException(404)`: If the user is not found.
    - `HTTPException(400)`: If the user's email is already confirmed.

    ### Example
    - Request: [POST] `/api/v1/contacts/request_email`"""
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"massage": "Your email is already confirmed."}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"massage": "Check your email for confirmation."}
