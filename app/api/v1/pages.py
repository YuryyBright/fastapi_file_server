from functools import wraps
from typing import Annotated, Union

from fastapi import APIRouter, Header, Request, Response, status, Depends
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.api.utils.do_file import get_system_stats
from app.managers.auth import oauth2_schema
from app.config.helpers import get_project_root

router = APIRouter(tags=["Pages"])

template_folder = get_project_root() / "app" / "templates"
templates = Jinja2Templates(directory=template_folder)
RootResponse = Union[dict[str, str], _TemplateResponse]
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
@router.get("/login",name="login_form",include_in_schema=False,response_class=HTMLResponse)
async def login(request: Request):
    """Login form"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/", include_in_schema=False, response_model=None,dependencies=[Depends(oauth2_schema)])
def root_path(
    request: Request,
    accept: Annotated[Union[str, None], Header()] = "text/html",
) -> Annotated[Union[RootResponse], RedirectResponse]:
    """Display an HTML template for a browser, JSON response otherwise."""


    if not request.cookies.get("access_token"):
        # Redirect to login page if refresh_token is missing
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    stats = get_system_stats()
    if stats:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "cpu_usage": stats["cpu_usage"],
            "total_files": stats["total_files"],
            "total_folders": stats["total_folders"],
            "total_size": stats["total_size"],
            "used_memory": stats["used_memory"],
            "total_memory": stats["total_memory"],
        })
    else:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "cpu_usage":0,
            "total_files": 0,
            "total_folders": 0,
            "total_size": 0,
            "used_memory":0,
            "total_memory":0,
        })


@router.get("/users/", include_in_schema=False, response_model=None, dependencies=[Depends(oauth2_schema)])
async def users(
    request: Request,
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
) -> Union[RedirectResponse, Response]:
    """
    Display an HTML template for browsers, or a JSON response for other request types.
    Check for the presence of refresh_token in cookies.
    """
    if not request.cookies.get("refresh_token"):
        # Redirect to login page if refresh_token is missing
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("file_manager/files.html", {"request": request})
