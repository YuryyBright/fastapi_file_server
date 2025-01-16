"""Main file for the FastAPI Template."""

import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from rich import print as rprint
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


from app.config.helpers import get_api_version, get_project_root
from app.config.settings import get_settings
from app.database.db import async_session, Base
from app.api import config_error
from app.api.routes import api_router
from app.api.config_error import not_found_handler, forbidden_handler, internal_server_error_handler

BLIND_USER_ERROR = 66
settings = get_settings()
# gatekeeper to ensure the user has read the docs and noted the major changes
# since the last version.
if not get_settings().i_read_the_damn_docs:
    print(
        "\n[red]ERROR:    [bold]You didn't read the docs and change the "
        "settings in the .env file!\n"
        "\nThe API has changed massively since version 0.4.0 and you need to "
        "familiarize yourself with the new breaking changes.\n"
        "\nSee https://api-template.seapagan.net/important/ for information.\n"
    )
    sys.exit(BLIND_USER_ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """Lifespan function Replaces the previous startup/shutdown functions.

    Currently we only ensure that the database is available and configured
    properly. We disconnect from the database immediately after.
    """
    try:
        async with async_session() as session:
            await session.connection()

        rprint("[green]INFO:     [/green][bold]Database configuration Tested.")
    except SQLAlchemyError as exc:
        rprint(f"[red]ERROR:    [bold]Have you set up your .env file?? ({exc})")
        rprint(
            "[yellow]WARNING:  [/yellow]Clearing routes and enabling "
            "error message."
        )
        app.routes.clear()
        app.include_router(config_error.router)

    yield
    # we would normally put any cleanup code here, but we don't have any at the

# DATABASE_URL = (
#         "postgresql://"
#         f"{get_settings().db_user}:{get_settings().db_password}@"
#         f"{get_settings().db_address}:{get_settings().db_port}/"
#         f"{get_settings().db_name}"
#     )
#     # moment so we just yield.
#
# Base.metadata.create_all(bind=create_engine(DATABASE_URL, echo=False))
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    redoc_url=None,
    docs_url=f"{settings.api_root}/docs",
    license_info=settings.license_info,
    contact=settings.contact,
    version=get_api_version(),
    lifespan=lifespan,
    swagger_ui_parameters={"defaultModelsExpandDepth": 0},
)

app.include_router(api_router)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(401, forbidden_handler)
app.add_exception_handler(500, internal_server_error_handler)
static_dir = get_project_root() /"app"/"static"
app.mount(
    f"{get_settings().api_root}/static",
    StaticFiles(directory=static_dir),
    name="static",
)

# set up CORS
cors_list = (get_settings().cors_origins).split(",")



app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)