import contextlib
from contextvars import ContextVar

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

from .settings import settings


class ScyllaDB:
    def __init__(self, server, auth=None) -> None:
        auth_provider = None
        if auth:
            auth_provider = PlainTextAuthProvider(username=auth[0], password=auth[1])
        self.cluster = Cluster([server], auth_provider=auth_provider)
        self._session = ContextVar("session")

    @property
    def session(self):
        return self._session

    @contextlib.contextmanager
    def make_session(self, keyspace):
        token = self._session.set(self.cluster.connect(keyspace))
        yield self._session.get()
        self._session.get().shutdown()
        self._session.reset(token)


scylladb = ScyllaDB(settings.SCYLLADB_SERVER, settings.SCYLLADB_AUTH)
