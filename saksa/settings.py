import os
import pathlib

from dotenv import load_dotenv


class Setting:
    def __init__(self, env_path) -> None:
        default_env_path = "/etc/saksa/.env"
        user_env_path = os.path.expanduser("~") + ".config/saksa/.env"
        load_dotenv(default_env_path)
        load_dotenv(user_env_path)
        load_dotenv(env_path)

    @property
    def KAFKA_BOOTSTRAP_SERVERS(self):
        return os.environ.get("KAFKA_BOOTSTRAP_SERVERS") or "localhost:9093"

    @property
    def ENV(self):
        return os.environ.get("SAKSA_ENV") or "production"

    @property
    def IS_PROD(self):
        return self.ENV == "production"

    @property
    def BASE_DIR(self):
        return pathlib.Path(__file__).resolve().parent

    @property
    def _BASE_TEMPLATE_DIR(self):
        return (
            self.BASE_DIR.joinpath("static/templates")
            if self.IS_PROD
            else self.BASE_DIR.joinpath("../templates")
        )

    @property
    def TEMPLATE_DIR(self):
        return "file://" + str(self._BASE_TEMPLATE_DIR)

    @property
    def INDEX_TEMPLATE_DIR(self):
        return (
            "file://" + str(self._BASE_TEMPLATE_DIR.joinpath(".."))
            if self.IS_PROD
            else "http://localhost:3000"
        )

    @property
    def SCYLLADB_SERVER(self):
        return os.environ.get("SCYLLADB_SERVER") or "localhost"

    @property
    def SCYLLADB_AUTH(self):
        username = os.environ.get("SCYLLADB_USERNAME")
        pwd = os.environ.get("SCYLLADB_PASSWORD")
        if username and pwd:
            return (username, pwd)
        return None

    @property
    def DISABLE_SECURE_COOKIES(self):
        return os.environ.get("DISABLE_SECURE_COOKIES", "").lower() in [
            "true",
            "1",
            "enable",
        ]


settings = Setting("./.env")
