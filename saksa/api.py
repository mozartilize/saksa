from accept_types import get_best_match
from cassandra.util import datetime_from_uuid1
from confluent_kafka.admin import AdminClient, NewTopic
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import HTTPConnection, Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route, Mount
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.templating import Jinja2Templates

from .auth.enpoints import AuthHtml
from .message_service import get_messages_list, handle_send_message
from .chatlist_service import get_chatlist_for_user
from .response import OrjsonResponse
from .settings import settings
from .scylladb import scylladb


class AuthVerificationAPI(HTTPEndpoint):
    async def get(self, request):
        return Response(status_code=204)


class UsersAPI(HTTPEndpoint):
    async def post(self, request):
        form = await request.form()
        username = form["username"]
        with scylladb.make_session("saksa") as scylla_session:
            future = scylla_session.execute_async(
                "INSERT INTO users(username) VALUES (%s) IF NOT EXISTS",
                (form["username"],),
            )
            result = future.result().one()
        if result.applied:
            kafka_client = AdminClient(
                {"bootstrap.servers": settings.kafka_bootstrap_servers}
            )
            fs = kafka_client.create_topics(
                [NewTopic(username, num_partitions=1, replication_factor=1)]
            )
            for _, f in fs.items():
                f.result()
            return OrjsonResponse(None, status_code=201)
        else:
            return OrjsonResponse(
                {"error": f'User "{form["username"]}" exists.'}, status_code=422
            )


class MessagesAPI(HTTPEndpoint):
    async def get(self, request: Request):
        with scylladb.make_session("saksa") as scylla_session:
            message_rows = await get_messages_list(
                scylla_session, chat_id=request.query_params["chat_id"]
            )
            data = []
            for message_row in message_rows.all():
                message_dict = message_row._asdict()
                message_dict["created_at"] = datetime_from_uuid1(
                    message_dict["created_at"]
                ).timestamp()
                data.append(message_dict)
            return OrjsonResponse(data)

    async def post(self, request: Request):
        content_type = request.headers["content-type"]
        if "form" in content_type:
            form = await request.form()
        elif "json" in content_type:
            form = await request.json()
        else:
            raise HTTPException(status_code=400)
        with scylladb.make_session("saksa") as scylla_session:
            await handle_send_message(scylla_session, form)
        return OrjsonResponse(None, status_code=201)


class ChatListAPI(HTTPEndpoint):
    async def get(self, request: Request):
        with scylladb.make_session("saksa") as scylla_session:
            chatlist_rows = await get_chatlist_for_user(
                scylla_session, request.user.username
            )
            data = []
            for chat_row in chatlist_rows.all()[::-1]:
                chat = chat_row._asdict()
                data.append(
                    {
                        "chat_id": chat["chat_id"],
                        "latest_message_sent_at": datetime_from_uuid1(
                            chat["latest_message_sent_at"]
                        ).timestamp(),
                        "latest_message": chat["latest_message"],
                    }
                )
            return OrjsonResponse(data)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        username = conn.cookies.get("username")
        if username:
            return AuthCredentials(["authenticated"]), SimpleUser(username)
        raise AuthenticationError("Invalid auth credentials.")


def auth_error_handler(conn: HTTPConnection, exc: Exception) -> Response:
    if (
        get_best_match(conn.headers["accept"], ["text/html", "application/json"])
        == "text/html"
    ):
        return RedirectResponse("/login", status_code=301)
    return Response(status_code=401)


class IndexHtml(HTTPEndpoint):
    async def get(self, request: Request):
        templates = Jinja2Templates(directory=settings.INDEX_TEMPLATE_DIR)
        return templates.TemplateResponse("index.html", context={"request": request})


api_routes = Mount(
    "/api/v1",
    routes=[
        Route("/messages", endpoint=MessagesAPI),
        Route("/users", endpoint=UsersAPI),
        Route("/chat", endpoint=ChatListAPI),
        Route("/auth/verify", endpoint=AuthVerificationAPI),
    ],
)
api_routes.app = AuthenticationMiddleware(api_routes.app, backend=BasicAuthBackend(), on_error=auth_error_handler)
login_route = Route("/login", endpoint=AuthHtml)
index_route = Route("/", endpoint=IndexHtml)
index_route.app = AuthenticationMiddleware(index_route.app, backend=BasicAuthBackend(), on_error=auth_error_handler)


routes = [api_routes, login_route, index_route]

api = Starlette(routes=routes)
