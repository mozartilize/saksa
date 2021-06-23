import os

from dotenv import load_dotenv


class Setting:
    def __init__(self, env_path) -> None:
        load_dotenv(env_path)

    @property
    def kafka_bootstrap_servers(self):
        return os.environ.get("KAFKA_BOOTSTRAP_SERVERS") or "127.0.0.1"
