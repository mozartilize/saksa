import asyncio

import socketio
import trio

from .aio_consumer import AIOConsumer, ConsumerExecutor
from .api import api
from .processors import EmitComsumedMessage
from .settings import settings
from .sio import create_sio


def start_consume_user_events(sio, server_stop_scope, server_stop_event, cout):
    loop = asyncio.get_running_loop()

    async def consume_user_events_loop():
        print("start consume_user_events_loop")
        with server_stop_scope:
            async with trio.open_nursery() as nursery:
                while not server_stop_event.is_set():
                    print("receiving...")
                    sid = await cout.receive()
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
                        consumer_exec.add_handler(EmitComsumedMessage(sio, sid))
                        session_data["consumer_exec"] = consumer_exec
                        await sio.save_session(sid, session_data)
                        nursery.start_soon(consumer_exec.run, nursery)
                    except Exception as e:
                        print(e)

    trio.lowlevel.start_guest_run(
        consume_user_events_loop,
        run_sync_soon_threadsafe=loop.call_soon_threadsafe,  # type: ignore
        run_sync_soon_not_threadsafe=loop.call_soon,  # type: ignore
        done_callback=lambda _: print("trio_main done!"),
        host_uses_signal_set_wakeup_fd=True,
    )


httpx_client = None
if settings.ENV == "development":
    import httpx
    import engineio

    def _get_static_file(path, static_files):
        if (
            path == "/"
            or path.startswith("/frontend")
            or path.startswith("/@")
            or path.startswith("/node_modules")
        ):
            static_file_dict = {"filename": settings.BASE_DIR.joinpath("../index.html")}
            static_file_dict["fe_path"] = path
            return static_file_dict
        return None

    engineio.async_drivers.asgi.get_static_file = _get_static_file  # type: ignore
    httpx_client = httpx.AsyncClient()


class ASGIApp(socketio.ASGIApp):
    async def _serve_static_file_dev(self, static_file, receive, send):
        event = await receive()
        if event["type"] == "http.request":
            static_file_resp = await httpx_client.get(  # type: ignore
                "http://localhost:3000" + static_file["fe_path"]
            )
            await send(
                {
                    "type": "http.response.start",
                    "headers": static_file_resp.headers.multi_items(),
                    "status": static_file_resp.status_code,
                }
            )
            async for chunk in static_file_resp.aiter_bytes():
                await send(
                    {
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    }
                )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"",
                }
            )

    if settings.ENV == "development":
        serve_static_file = _serve_static_file_dev


def create_app():
    cin: trio.MemorySendChannel
    cout: trio.MemoryReceiveChannel
    cin, cout = trio.open_memory_channel(1000)
    server_stop_event = trio.Event()
    server_stop_scope = trio.CancelScope()

    def on_startup():
        start_consume_user_events(sio, server_stop_scope, server_stop_event, cout)

    def on_shutdown():
        print("sending stop event to trio loop...")
        server_stop_event.set()
        server_stop_scope.cancel()

    sio = create_sio(cin, cout)
    app = ASGIApp(
        sio,
        other_asgi_app=api,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        static_files={
            "/": str(settings.BASE_DIR.joinpath("static/index.html")),
            "/assets": str(settings.BASE_DIR.joinpath("static/assets")),
        },
    )
    return app
