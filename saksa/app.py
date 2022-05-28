import asyncio
import pathlib

import socketio
from socketio.exceptions import ConnectionRefusedError
import trio

from .aio_consumer import AIOConsumer, ConsumerExecutor
from .api import api
from .settings import Setting

BASE_DIR = pathlib.Path(__file__).parent

settings = Setting("./.env")

sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)

# redis = aioredis.from_url(settings.redis_url)

cin: trio.MemorySendChannel
cout: trio.MemoryReceiveChannel
cin, cout = trio.open_memory_channel(100)
server_stop_event = trio.Event()
server_stop_scope = trio.CancelScope()


def start_trio_loop():
    loop = asyncio.get_running_loop()
    trio.lowlevel.start_guest_run(
        trio_main,
        run_sync_soon_threadsafe=loop.call_soon_threadsafe,
        run_sync_soon_not_threadsafe=loop.call_soon,
        done_callback=lambda _: print("trio_main done!"),
        host_uses_signal_set_wakeup_fd=True,
    )


async def trio_main():
    with server_stop_scope:
        async with trio.open_nursery() as nursery:
            while not server_stop_event.is_set():
                print("receiving...")
                ok_check: asyncio.Queue
                sid, ok_check = await cout.receive()
                print(f"received sid={sid}")
                try:
                    c = AIOConsumer(
                        {
                            "bootstrap.servers": settings.kafka_bootstrap_servers,
                            "group.id": sid,
                            "auto.offset.reset": "largest",
                        }
                    )
                    session_data = await sio.get_session(sid)
                    await c.subscribe(session_data["topics"])
                    consumer_exec = ConsumerExecutor(sid, c)
                    consumer_exec.add_handler(PrintMessageHandler())
                    session_data["consumer_exec"] = consumer_exec
                    await sio.save_session(sid, session_data)
                    nursery.start_soon(consumer_exec.run, nursery)
                    ok_check.put_nowait(True)
                except Exception as e:
                    print(e)
                    ok_check.put_nowait(e)


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
    # if "token" not in auth:
    #     raise ConnectionRefusedError("Unauthorize.")
    # ok = redis.delete(auth["token"])
    # if not ok:
    #     raise ConnectionRefusedError("Unauthorize.")
    # decoded_token = decode_auth_token(auth["token"])
    topics = ["mytopic"]
    await sio.save_session(sid, {"topics": topics})
    ok_check = asyncio.Queue(1)
    cin.send_nowait((sid, ok_check))
    ok = await ok_check.get()
    if isinstance(ok, Exception):
        raise ConnectionAbortedError()
    elif not ok:
        raise ConnectionRefusedError()


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


app = socketio.ASGIApp(
    sio,
    other_asgi_app=api,
    on_startup=start_trio_loop,
    on_shutdown=on_app_stop,
    static_files={
        "/": str(BASE_DIR.joinpath("index.html")),
        "/static": str(BASE_DIR.joinpath("static")),
    }
)
