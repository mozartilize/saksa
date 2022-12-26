import os
import pathlib

from dotenv import load_dotenv


class Setting:
    def __init__(self, env_path) -> None:
        load_dotenv(env_path)

    @property
    def kafka_bootstrap_servers(self):
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
    def DEBUG(self):
        env_var = os.environ.get("SAKSA_DEBUG") or "0"
        return env_var.lower() in ["true", 1, "enabled"]

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
        return "file://" + str(
            self._BASE_TEMPLATE_DIR.joinpath("..")
            if self.IS_PROD
            else "http://localhost:3000"
        )

    @property
    def SCYLLADB_SERVER(self):
        return os.environ.get("SCYLLADB_SERVER") or "localhost"


settings = Setting("./.env")
