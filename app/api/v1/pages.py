from functools import wraps
from typing import Annotated, Union

from fastapi import APIRouter, Header, Request, Response, status, Depends
from starlette.responses import HTMLResponse, RedirectResponse

from api import templates, RootResponse
from config.helpers import get_api_version
from config.settings import get_settings
from managers.auth import oauth2_schema
router = APIRouter(tags=["Pages"])


# # Custom decorator to check for refresh token
# def check_refresh_token_decorator(func):
#     """
#     Decorator to check if the refresh_token is present in cookies.
#     If not, redirects the user to the login page.
#     """
#     @wraps(func)
#     async def wrapper(request: Request, *args, **kwargs):
#         if not request.cookies.get("refresh_token"):
#             # Redirect to login page if refresh_token is missing
#             return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
#         # Викликаємо функцію, що обробляє запит асинхронно
#         return await func(request, *args, **kwargs)
#     return wrapper
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Login form"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/", include_in_schema=False, response_model=None)
def root_path(
    request: Request,
    accept: Annotated[Union[str, None], Header()] = "text/html",
) -> Annotated[Union[RootResponse], RedirectResponse]:
    """Display an HTML template for a browser, JSON response otherwise."""
    if not request.cookies.get("refresh_token"):
        # Redirect to login page if refresh_token is missing
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


@router.get("/users/", include_in_schema=False, response_model=None, dependencies=[Depends(oauth2_schema)])
async def users(
    request: Request,
    accept: Union[str, None] = Header(default="text/html"),
) -> Union[RedirectResponse, Response]:
    """
    Display an HTML template for browsers, or a JSON response for other request types.
    Check for the presence of refresh_token in cookies.
    """
    if not request.cookies.get("refresh_token"):
        # Redirect to login page if refresh_token is missing
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("user/users.html", {"request": request})


@router.get("/files/", include_in_schema=False, response_model=None, dependencies=[Depends(oauth2_schema)])
async def files(
    request: Request,
    accept: Union[str, None] = Header(default="text/html"),
) -> Union[RedirectResponse, Response]:
    """
    Display an HTML template for browsers, or a JSON response for other request types.
    Check for the presence of refresh_token in cookies.
    """
    if not request.cookies.get("refresh_token"):
        # Redirect to login page if refresh_token is missing
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("file_manager/files.html", {"request": request})
