import logging

import anyio
import socketio

from .api import api
from .settings import settings
from .sio import create_sio

logger = logging.getLogger(__name__)


httpx_client = None
if settings.ENV == "development":
    import httpx
    import engineio

    def _get_static_file(path, static_files):
        if (path.startswith("/frontend")
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
    sio = create_sio()
    app = ASGIApp(
        sio,
        other_asgi_app=api,
        static_files={
            "/assets": str(settings.BASE_DIR.joinpath("static/assets")),
        },
    )
    return app
