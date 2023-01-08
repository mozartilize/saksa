from confluent_kafka.admin import AdminClient, NewTopic
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from saksa.libs.templates import Jinja2Templates
from saksa.scylladb import scylladb
from saksa.settings import settings

from .auth_service import create_user


class AuthAPI(HTTPEndpoint):
    def post(self, request: Request):
        pass


class AuthHtml(HTTPEndpoint):
    async def get(self, request: Request):
        templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
        return templates.TemplateResponse(
            "/auth/index.html", context={"request": request}
        )

    async def post(self, request: Request):
        form = await request.form()
        username = form["username"]
        with scylladb.make_session("saksa") as session:
            fut = await create_user(session, username)
            result = fut.one()
        if result.applied:
            kafka_client = AdminClient(
                {"bootstrap.servers": settings.kafka_bootstrap_servers}
            )
            fs = kafka_client.create_topics(
                [NewTopic(username, num_partitions=1, replication_factor=1)]
            )
            for _, f in fs.items():
                f.result()
        resp = RedirectResponse("/", status_code=301)
        resp.set_cookie(
            "username", username, secure=not settings.DISABLE_SECURE_COOKIES
        )
        return resp
