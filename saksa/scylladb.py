import contextlib
from contextvars import ContextVar

from cassandra.cluster import Cluster

from .settings import settings


class ScyllaDB:
    def __init__(self, server) -> None:
        self.cluster = Cluster([server])
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


scylladb = ScyllaDB(settings.SCYLLADB_SERVER)
