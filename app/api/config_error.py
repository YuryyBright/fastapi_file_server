from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config.helpers import get_project_root

template_folder = get_project_root() / "app" / "templates"
templates = Jinja2Templates(directory=template_folder)


# 404 Not Found
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


# 403 Forbidden
async def forbidden_handler(request: Request, exc):
    return templates.TemplateResponse("403.html", {"request": request}, status_code=401)


# 500 Internal Server Error
async def internal_server_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)