import contextlib
from cassandra.cluster import Cluster


class ScyllaDB:
    def __init__(self, server) -> None:
        self.cluster = Cluster([server])
        self._session = None

    @property
    def session(self):
        return self._session

    @contextlib.contextmanager
    def make_session(self, keyspace):
        self._session = self.cluster.connect(keyspace)
        yield self._session
        self._session.close()
        self._session = None
