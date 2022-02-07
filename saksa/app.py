import asyncio

import aioredis
import socketio
from socketio.exceptions import ConnectionRefusedError
import trio

from .aio_consumer import AIOConsumer, ConsumerExecutor
from .settings import Setting

sio = socketio.AsyncServer(async_mode="asgi")
settings = Setting("./.env")

redis = aioredis.from_url(settings.redis_url)
cin, cout = trio.open_memory_channel(100)

server_stop_event = trio.Event()
server_stop_scope = trio.CancelScope()


def start_trio_loop():
    loop = asyncio.get_event_loop()

    trio.lowlevel.start_guest_run(
        trio_main,
        run_sync_soon_threadsafe=loop.call_soon_threadsafe,
    )


async def trio_main():
    with server_stop_scope:
        async with trio.open_nursery() as nursery:
            while not server_stop_event.is_set():
                consumer = await cout.receive()
                nursery.start_soon(consumer.run, nursery)


class PrintMessageHandler:
    def process(self, msg):
        if msg.error():
            print(f"Got error: {msg.error()}")
        else:
            print(msg.value())


class EmitComsumedMessage:
    def __init__(self, sio: socketio.AsyncServer, sid: str):
        self._sio = sio
        self._sid = sid

    async def process(self, msg):
        await self._sio.send(msg.value(), room=self._sid)


class ErrorProcessor:
    async def process(self, msg):
        await trio.sleep(0.5)
        raise Exception("error")


def decode_auth_token(token) -> dict:
    return {}


@sio.event
async def connect(sid, environ, auth):
    if "token" not in auth:
        raise ConnectionRefusedError("Unauthorize.")
    ok = redis.delete(auth["token"])
    if not ok:
        raise ConnectionRefusedError("Unauthorize.")
    decoded_token = decode_auth_token(auth["token"])
    c = AIOConsumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": sid,
            "auto.offset.reset": "largest",
        }
    )
    await c.subscribe([decoded_token["uid"]])
    consumer_exec = ConsumerExecutor(sid, c)
    consumer_exec.add_handler(EmitComsumedMessage(sio, sid))
    await sio.save_session(sid, {"consumer_exec": consumer_exec})
    await cin.send(consumer_exec)


@sio.event
async def disconnect(sid):
    session_data = await sio.get_session(sid)
    consumer_exec = session_data["consumer_exec"]
    consumer_exec.stop()
    print(f"{sid} disconnects")


def on_app_stop():
    print("sending stop event to trio loop...")
    server_stop_event.set()
    server_stop_scope.cancel()


app = socketio.ASGIApp(sio, on_startup=start_trio_loop, on_shutdown=on_app_stop)
