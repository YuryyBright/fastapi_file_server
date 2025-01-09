"""Routes for the home screen and templates."""

from typing import Annotated, Union

from fastapi import APIRouter, Header, Request, Depends, status, Response

from managers.auth import oauth2_schema
from schemas.base import LogoutResponse

router = APIRouter(tags=["Home"])

@router.get(
    "/logout/",
    name="logout_user",
    dependencies=[Depends(oauth2_schema)],
    status_code=status.HTTP_200_OK,
    response_model=LogoutResponse
)
async def logout(response: Response):
    """Logout the user by clearing the authentication tokens in cookies."""
    # Remove the cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    # Return a response indicating logout was successful
    return {"message": "User logged out successfully"}