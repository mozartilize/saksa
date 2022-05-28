import uuid
from datetime import datetime

from cassandra.util import max_uuid_from_time

from .aio import async_

@async_
def create_message(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO messages(chat_id, sender, message, created_at) VALUES (%s, %s, %s, %s)",
        (
            uuid.UUID(data["chat_id"]),
            data["sender"],
            data["message"],
            max_uuid_from_time(datetime.utcnow()),
        ),
    )
    return future
