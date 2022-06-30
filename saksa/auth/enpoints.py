from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from saksa.settings import settings


class AuthAPI(HTTPEndpoint):
    def post(self, request: Request):
        pass


class AuthHtml(HTTPEndpoint):
    async def get(self, request: Request):
        templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
        return templates.TemplateResponse(
            "auth/index.html", context={"request": request}
        )

    async def post(self, request: Request):
        form = await request.form()
        resp = RedirectResponse("/")
        resp.set_cookie("username", form["username"], secure=True)
        return resp
