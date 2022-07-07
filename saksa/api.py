from cassandra.cluster import Cluster
from cassandra.util import datetime_from_uuid1
from confluent_kafka.admin import AdminClient, NewTopic
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.exceptions import HTTPException

from .auth.enpoints import AuthHtml
from .message_service import get_messages_list, handle_send_message
from .response import OrjsonResponse
from .settings import settings

cluster = Cluster(["127.0.0.1"], port=9042)
scylla = cluster.connect("saksa")


class UsersAPI(HTTPEndpoint):
    async def post(self, request):
        form = await request.form()
        username = form["username"]
        future = scylla.execute_async(
            "INSERT INTO users(username) VALUES (%s) IF NOT EXISTS", (form["username"],)
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
        message_rows = await get_messages_list(
            scylla, chat_id=request.query_params["chat_id"]
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
        await handle_send_message(scylla, form)
        return OrjsonResponse(None, status_code=201)


class ChatAPI(HTTPEndpoint):
    async def get(self, request: Request):
        pass


routes = [
    Mount(
        "/api/v1",
        routes=[
            Route("/messages", endpoint=MessagesAPI),
            Route("/users", endpoint=UsersAPI),
        ],
    ),
    Route("/login", endpoint=AuthHtml),
]
api = Starlette(routes=routes)
