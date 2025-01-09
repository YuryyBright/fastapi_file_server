"""Define routes for Authentication."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse


from app.database.db import get_database
from app.managers.auth import AuthManager
from app.managers.user import UserManager
from app.schemas.request.auth import TokenRefreshRequest
from app.schemas.request.user import UserLoginRequest, UserRegisterRequest
from app.schemas.response.auth import TokenRefreshResponse, TokenResponse


from typing import Annotated, Union

from fastapi import APIRouter, Header, Request, Response
router = APIRouter(tags=["Authentication"])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    name="register_a_new_user",
    response_model=TokenResponse,
)
async def register(
    background_tasks: BackgroundTasks,
    user_data: UserRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
) -> dict[str, str]:
    """Register a new User and return a JWT token plus a Refresh Token.

    The JWT token should be sent as a Bearer token for each access to a
    protected route. It will expire after 120 minutes.

    When the JWT expires, the Refresh Token can be sent using the '/refresh'
    endpoint to return a new JWT Token. The Refresh token will last 30 days, and
    cannot be refreshed.
    """
    token, refresh = await UserManager.register(
        user_data.model_dump(),
        session=session,
        background_tasks=background_tasks,
    )
    return {"token": token, "refresh": refresh}


@router.post(
    "/login/",
    name="login_an_existing_user",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    user_data: UserLoginRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
    response: Response,  # Ensure the response object is included to set cookies
    request: Request  # To access cookies in the request
) -> dict[str, str]:
    """
    Login an existing User and return a JWT token plus a Refresh Token.

    The JWT token should be sent as a Bearer token for each access to a
    protected route. It will expire after 120 minutes.

    When the JWT expires, the Refresh Token can be sent using the '/refresh'
    endpoint to return a new JWT Token. The Refresh token will last 30 days, and
    cannot be refreshed.
    """
    # Check if the user is already logged in


    # Authenticate user and retrieve tokens
    token, refresh = await UserManager.login(user_data.model_dump(), session)

    # Set tokens in cookies for subsequent requests
    response.set_cookie(
        "refresh_token", refresh, httponly=True, secure=True, samesite="Strict", max_age=60 * 60 * 24 * 30  # 30 days
    )
    response.set_cookie(
        "access_token", token, httponly=True, secure=True, samesite="Strict", max_age=60 * 60 * 24 * 30  # 30 days
    )

    # Return the tokens in the response body as well (use TokenResponse model for response)
    return {"token": token, "refresh": refresh}




@router.post(
    "/refresh/",
    name="refresh_an_expired_token",
    response_model=TokenRefreshResponse,
)
async def generate_refresh_token(
    refresh_token: TokenRefreshRequest,
    session: Annotated[AsyncSession, Depends(get_database)],
) -> dict[str, str]:
    """Return a new JWT, given a valid Refresh token.

    The Refresh token will not be updated at this time, it will still expire 30
    days after original issue. At that time the User will need to login again.
    """
    token = await AuthManager.refresh(refresh_token, session)
    return {"token": token}


@router.get("/verify/", status_code=status.HTTP_200_OK)
async def verify(
    session: Annotated[AsyncSession, Depends(get_database)], code: str = ""
) -> None:
    """Verify a new user.

    The code is sent to  new user by email, which must then be validated here.

    We dont need to return anything here, as success or errors will be handled
    by FastAPI exceptions.
    """
    await AuthManager.verify(code, session)


# @router.get("/resend/", status_code=status.HTTP_200_OK)
# async def resend_verify_code(background_tasks: BackgroundTasks, user: int):
#     """Re-send a verification code to the specified user.

#     Can be used in the event that the original code expires.
#     """
#     response = await AuthManager.resend_verify_code(
#         user, background_tasks=background_tasks
#     )
#     return response
