"""Include all the other routes into one router."""

from fastapi import APIRouter

from app.config.settings import get_settings
from app.api.v1 import auth, home, user, pages, file,folder

api_router = APIRouter(prefix=get_settings().api_root)

api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(pages.router)
api_router.include_router(file.file)
api_router.include_router(folder.folder)

if not get_settings().no_root_route:
    api_router.include_router(home.router)
