from jinja2 import Environment

from starlette.templating import Jinja2Templates as _Jinja2Templates, pass_context

from .loaders import SaksaTemplateLoader


class Jinja2Templates(_Jinja2Templates):
    def _create_env(self, directory, **env_options):
        @pass_context
        def url_for(context: dict, name: str, **path_params) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        loader = SaksaTemplateLoader(directory)
        env_options.setdefault("loader", loader)
        env_options.setdefault("autoescape", True)

        env = Environment(**env_options)
        env.globals["url_for"] = url_for
        return env


__all__ = ["Jinja2Templates"]
