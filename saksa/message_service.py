import uuid
from datetime import datetime

from cassandra import ConsistencyLevel
from cassandra.query import BatchStatement
from cassandra.util import max_uuid_from_time

from .aio import async_


@async_
def create_chat(scylladb, members):
    future = scylladb.execute_async(
        "INSERT INTO chats_and_members(chat_id, members) VALUES (uuid(), %s)",
        (
            members,
        ),
    )
    return future


@async_
def create_chats_by_users(scylladb, chat_id, members, latest_message, latest_message_sent_at):
    insert_stmt = scylladb.prepare("INSERT INTO chats_by_user(username, chat_id, latest_message, latest_message_sent_at) VALUES (?, ?, ?, ?)")
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

    for username in members:
        batch.add(insert_stmt, chat_id, username, latest_message, latest_message_sent_at)
    return scylladb.execute_async(batch)


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


@async_
def get_messages_list(scylladb, chat_id):
    future = scylladb.execute_async(
        "SELECT * FROM messages WHERE chat_id = %s",
        (
            uuid.UUID(chat_id),
        ),
    )
    return future