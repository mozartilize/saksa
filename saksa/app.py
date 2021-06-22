import contextvars

import socketio

from .aio_consumer import AIOConsumer

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

consumer_ctx = contextvars.ContextVar('consumer')


@sio.event
async def connect(sid, environ, auth):
    print(f"{sid} connected with env={environ}; auth={auth}")
    await sio.save_session(sid, auth)
    consumer_ctx.set(AIOConsumer({}))


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