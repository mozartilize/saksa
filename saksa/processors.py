import anyio
import socketio


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
        await anyio.sleep(0.5)
        raise Exception("error")
