from http import HTTPStatus

from jinja2 import TemplateNotFound
from jinja2.loaders import BaseLoader
from httpx import Client, HTTPStatusError

from saksa.libs.httpx_ext.transport import FileUriTransport


class SaksaTemplateLoader(BaseLoader):
    def __init__(self, base_url):
        self.client = Client(mounts={"file://": FileUriTransport()}, base_url=base_url)

    def get_source(self, environment, template: str):
        resp = self.client.get(template)
        try:
            resp.raise_for_status()
            return resp.text, None, None
        except HTTPStatusError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                raise TemplateNotFound(template)
            raise
