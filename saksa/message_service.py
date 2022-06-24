import uuid
from datetime import datetime

import trio
from cassandra import ConsistencyLevel
from cassandra.cluster import ResultSet
from cassandra.query import BatchStatement
from cassandra.util import max_uuid_from_time

from .aio import async_, trio_to_asyncio, trio_async_


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


@trio_async_
def create_message(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO messages(chat_id, sender, message, created_at) VALUES (%s, %s, %s, %s)",
        (
            uuid.UUID(data["chat_id"]),
            data["sender"],
            data["message"],
            max_uuid_from_time(datetime.fromtimestamp(data["created_at"]/1000)) if data.get("created_at") else max_uuid_from_time(datetime.utcnow()),
        ),
    )
    return future


@trio_async_
def create_users_latest_chat(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO chats_by_user(username, latest_message_sent_at, chat_id, latest_message) VALUES (%s, %s, %s, %s)",
        (
            data["username"],
            max_uuid_from_time(datetime.fromtimestamp(data["created_at"]/1000)) if data.get("created_at") else max_uuid_from_time(datetime.utcnow()),
            uuid.UUID(data["chat_id"]),
            data["message"],
        ),
    )
    return future


@trio_async_
def delete_users_latest_chat(scylladb, data):
    future = scylladb.execute_async(
        "DELETE FROM chats_by_user WHERE chat_id=%s AND username=%s AND latest_message_sent_at < %s",
        (
            uuid.UUID(data["chat_id"]),
            data["username"],
            max_uuid_from_time(datetime.fromtimestamp(data["created_at"]/1000)) if data.get("created_at") else max_uuid_from_time(datetime.utcnow()),
        ),
    )
    return future


@async_
def get_messages_list(scylladb, chat_id):
    future = scylladb.execute_async(
        "SELECT * FROM messages WHERE chat_id = %s ORDER BY created_at",
        (
            uuid.UUID(chat_id),
        ),
    )
    return future


@trio_async_
def get_chat_members(scylladb, chat_id):
    future = scylladb.execute_async(
        "SELECT members FROM chat_members WHERE chat_id = %s",
        (
            uuid.UUID(chat_id),
        ),
    )
    return future


@trio_to_asyncio
async def handle_send_message(scylladb, data):
    # TODO: use batch query
    members_result: ResultSet = await get_chat_members(scylladb, data["chat_id"])
    async with trio.open_nursery() as nursery:
        nursery.start_soon(create_message, scylladb, data)
        members = members_result.one()[0]
        for member in members:
            print(member)
            data = {**data, "username": member}
            nursery.start_soon(create_users_latest_chat, scylladb, data)
            nursery.start_soon(delete_users_latest_chat, scylladb, data)
