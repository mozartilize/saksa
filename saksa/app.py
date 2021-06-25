import threading

import socketio
import trio
import trio_asyncio

from .aio_consumer import AIOConsumer, ConsumerExecutor
from .settings import Setting

sio = socketio.AsyncServer(async_mode="asgi")
settings = Setting("./.env")

cin, cout = trio.open_memory_channel(100)

server_stop_event = trio.Event()
server_stop_scope = trio.CancelScope()

_TRIO_TOKEN = None


def start_trio_loop():
    t = threading.Thread(target=trio_asyncio.run, args=(trio_main,))
    t.start()


async def trio_main():
    global _TRIO_TOKEN
    _TRIO_TOKEN = trio.lowlevel.current_trio_token()
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
        await trio_asyncio.aio_as_trio(self._sio.send)(msg.value(), room=self._sid)


@sio.event
async def connect(sid, environ, auth):
    c = AIOConsumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": sid,
            "auto.offset.reset": "largest",
        }
    )
    print(_TRIO_TOKEN)
    await c.subscribe(["mytopic"])
    consumer_exec = ConsumerExecutor(sid, c)
    consumer_exec.add_handler(PrintMessageHandler())
    consumer_exec.add_handler(EmitComsumedMessage(sio, sid))
    await sio.save_session(sid, {"consumer_exec": consumer_exec})
    trio.from_thread.run(cin.send, consumer_exec, trio_token=_TRIO_TOKEN)


@sio.event
async def disconnect(sid):
    session_data = await sio.get_session(sid)
    consumer_exec = session_data["consumer_exec"]
    consumer_exec.stop()
    print(f"{sid} disconnects")


def on_app_stop():
    print("sending stop event to trio loop...")
    trio.from_thread.run_sync(server_stop_event.set, trio_token=_TRIO_TOKEN)
    trio.from_thread.run_sync(server_stop_scope.cancel, trio_token=_TRIO_TOKEN)


app = socketio.ASGIApp(sio, on_startup=start_trio_loop, on_shutdown=on_app_stop)
