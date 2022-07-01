import socketio


class IndexNamespace(socketio.AsyncNamespace):
    def __init__(
        self,
        namespace: str,
        cin,
        cout,
    ) -> None:
        super().__init__(namespace)
        self.cin = cin
        self.cout = cout

    async def on_connect(self, sid, environ, auth):
        topics = [auth["username"]]
        await self.save_session(sid, {"topics": topics})
        await self.cin.send(sid)

    async def on_disconnect(self, sid):
        session_data = await self.get_session(sid)
        consumer_exec = session_data.get("consumer_exec")
        consumer_exec.stop()

    async def on_my_event(self, sid, data):
        await self.emit("my_response", data)


def create_sio(cin, cout):
    sio = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
    sio.register_namespace(IndexNamespace("/", cin, cout))
    return sio
