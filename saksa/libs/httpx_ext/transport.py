import os
from http import HTTPStatus
from contextvars import ContextVar

from httpx._transports.base import BaseTransport
from httpx._transports.wsgi import WSGIByteStream
from httpx import Request, Response


class FileUriTransport(BaseTransport):
    def __init__(self):
        self.afp = ContextVar("afp")

    def handle_request(
        self,
        request: Request,
    ) -> Response:
        if not os.path.exists(request.url.path):
            return Response(status_code=HTTPStatus.NOT_FOUND)
        fo = open(request.url.path, "rb")
        self.afp.set(fo)
        return Response(
            status_code=HTTPStatus.OK,
            stream=WSGIByteStream(fo),
        )

    def close(self) -> None:
        self.afp.get().close()
