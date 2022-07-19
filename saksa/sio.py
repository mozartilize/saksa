import asyncio
import logging

import socketio

from .user_event_service import consume_user_events

logger = logging.getLogger(__name__)


class IndexNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        task, consumer_exec = await consume_user_events(self, sid, auth["username"])
        async with self.session(sid) as session:
            session["task"] = task
            session["consumer_exec"] = consumer_exec

    async def on_disconnect(self, sid):
        try:
            session_data = await self.get_session(sid)
            consumer_exec = session_data["consumer_exec"]
            consumer_exec.stop()
            task: asyncio.Task = session_data["task"]
            task.cancel()
        except KeyError:
            logger.info(f"{sid} connects error. Disconnecting...")

    async def on_my_event(self, sid, data):
        await self.emit("my_response", data)


def create_sio():
    sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
    sio.register_namespace(IndexNamespace("/"))
    return sio
