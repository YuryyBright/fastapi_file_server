"""Define all the resources (routes) for the API."""
from functools import wraps
from typing import Union

from starlette.templating import Jinja2Templates, _TemplateResponse

from config.helpers import get_project_root
from config.settings import get_settings
from managers.sessions import SessionManager

template_folder = get_project_root() / "app" / "templates"
templates = Jinja2Templates(directory=template_folder)
RootResponse = Union[dict[str, str], _TemplateResponse]

session_manager = SessionManager(secret_key=get_settings().secret_key, jwt_expiration=60*60*2, refresh_token_expiration=60*60*24*30)


