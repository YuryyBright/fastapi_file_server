"""Routes for the home screen and templates."""

from typing import Annotated, Union

from fastapi import APIRouter, Header, Request, Depends, status, Response
from fastapi.responses import RedirectResponse
from api import RootResponse, templates
from app.config.helpers import get_api_version, get_project_root
from app.config.settings import get_settings
from managers.auth import oauth2_schema
from schemas.base import LogoutResponse

router = APIRouter(tags=["Home"])
@router.get("/", include_in_schema=False, response_model=None)
def root_path(
    request: Request,
    accept: Annotated[Union[str, None], Header()] = "text/html",
) -> RootResponse:
    """Display an HTML template for a browser, JSON response otherwise."""
    if not request.cookies.get("refresh_token"):
        # Redirect to the main page if the user is already logged in
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    if accept and accept.split(",")[0] == "text/html":
        context = {
            "title": get_settings().api_title,
            "description": get_settings().api_description,
            "repository": get_settings().repository,
            "author": get_settings().contact["name"],
            "website": get_settings().contact["url"],
            "year": get_settings().year,
            "version": get_api_version(),
        }
        return templates.TemplateResponse(
            request=request, name="index.html", context=context
        )

    return {
        "info": (
            f"{get_settings().contact['name']}'s {get_settings().api_title}"
        ),
        "repository": get_settings().repository,
    }
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