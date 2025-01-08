"""Routes for the home screen and templates."""

from typing import Annotated, Union

from fastapi import APIRouter, Header, Request

from api import RootResponse, templates
from app.config.helpers import get_api_version, get_project_root
from app.config.settings import get_settings

router = APIRouter()
@router.get("/", include_in_schema=False, response_model=None)
def root_path(
    request: Request,
    accept: Annotated[Union[str, None], Header()] = "text/html",
) -> RootResponse:
    """Display an HTML template for a browser, JSON response otherwise."""
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
