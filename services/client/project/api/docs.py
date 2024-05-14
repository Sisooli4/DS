"""
Top-level routes to serve api documentation in openapi format and swagger ui.

Relates to the following top-level endpoints:
- `/docs`: Swagger ui version of the openapi spec returned by `/openapi.json`.
- `/openapi.json`: API description in openapi format, endpoint url configured
  as parameter of `app` object.
"""

from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from icecream import ic
router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def get_docs() -> HTMLResponse:
    """Return openapi documentation in interactive swagger ui format.

    :return: Interactive swagger ui page to browse openapi documentation.
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Client API documentation",
        swagger_js_url="/static/docs/swagger-ui-bundle.js",
        swagger_css_url="/static/docs/swagger-ui.css",
    )
