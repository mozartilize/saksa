import uuid
from datetime import datetime

from cassandra.cluster import Cluster
from cassandra.util import max_uuid_from_time
from confluent_kafka.admin import AdminClient, NewTopic
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

from .message_service import create_message, get_messages_list
from .settings import Setting

cluster = Cluster(["127.0.0.1"], port=9042)
scylla = cluster.connect("saksa")
settings = Setting("./.env")


class AuthAPI(HTTPEndpoint):
    async def post(self, request):
        pass


class UsersAPI(HTTPEndpoint):
    async def post(self, request):
        form = await request.form()
        username = form['username']
        future = scylla.execute_async(
            "INSERT INTO users(username) VALUES (%s) IF NOT EXISTS", (form["username"],)
        )
        result = future.result().one()
        if result.applied:
            kafka_client = AdminClient({"bootstrap.servers": settings.kafka_bootstrap_servers})
            fs = kafka_client.create_topics([NewTopic(username, num_partitions=1, replication_factor=1)])
            for _, f in fs.items():
                f.result()
            return JSONResponse(None, status_code=201)
        else:
            return JSONResponse(
                {"error": f'User "{form["username"]}" exists.'}, status_code=422
            )


class MessagesAPI(HTTPEndpoint):
    async def get(self, request: Request):
        messages = await get_messages_list(scylla, chat_id=request.query_params["chat_id"])
        import pdb; pdb.set_trace()
        return JSONResponse(messages.all())

    async def post(self, request: Request):
        form = await request.form()
        await create_message(scylla, form)
        return JSONResponse(None, status_code=201)


routes = [
    Mount(
        "/api/v1",
        routes=[
            Route("/messages", endpoint=MessagesAPI),
            Route("/users", endpoint=UsersAPI),
        ],
    )
]
api = Starlette(routes=routes)
