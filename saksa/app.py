import contextvars

import socketio

from .aio_consumer import AIOConsumer
from .settings import Setting

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)
settings = Setting("./.env")

consumer_ctx = contextvars.ContextVar('consumer')


@sio.event
async def connect(sid, environ, auth):
    print(f"{sid} connected with env={environ}; auth={auth}")
    await sio.save_session(sid, auth)
    consumner = AIOConsumer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": sid,
        'auto.offset.reset': 'largest',
    })
    consumer_ctx.set(consumner)
    consumner.subcribe(auth["topics"])


@sio.event
async def disconnect(sid):
    print(f"{sid} disconnects")
    consumer = consumer_ctx.get()
    consumer.close()


@sio.event
async def message(sid, data):
    print(data)
    auth = await sio.get_session(sid)
    print(auth)