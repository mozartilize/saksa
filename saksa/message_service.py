import uuid
from datetime import datetime, timezone

import anyio
from cassandra import ConsistencyLevel
from cassandra.cluster import ResultSet
from cassandra.query import BatchStatement
from cassandra.util import uuid_from_time

from .aio import async_


@async_
def create_chat_members(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO chat_members(chat_id, members) VALUES (%s, %s)",
        (uuid.UUID(data["chat_id"]), set(data["members"]))
    )
    return future


@async_
def create_chats_by_users(
    scylladb, chat_id, members, latest_message, latest_message_sent_at
):
    insert_stmt = scylladb.prepare(
        "INSERT INTO chats_by_user(username, chat_id, latest_message, latest_message_sent_at) VALUES (?, ?, ?, ?)"
    )
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)

    for username in members:
        batch.add(
            insert_stmt, chat_id, username, latest_message, latest_message_sent_at
        )
    return scylladb.execute_async(batch)


@async_
def create_message(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO messages(chat_id, sender, message, created_at) VALUES (%s, %s, %s, %s)",
        (
            uuid.UUID(data["chat_id"]),
            data["sender"],
            data["message"],
            uuid_from_time(
                datetime.fromtimestamp(data["created_at"]).replace(tzinfo=timezone.utc)
            )
            if data.get("created_at")
            else uuid_from_time(datetime.utcnow().replace(tzinfo=timezone.utc)),
        ),
    )
    return future


@async_
def get_users_latest_chat(scylladb, data):
    future = scylladb.execute_async(
        "SELECT * FROM chats_by_user WHERE username = %s AND chat_id = %s LIMIT 1",
        (
            data["username"],
            uuid.UUID(data["chat_id"]),
        ),
    )
    return future


@async_
def create_users_latest_chat(scylladb, data):
    future = scylladb.execute_async(
        "INSERT INTO chats_by_user(username, latest_message_sent_at, chat_id, name, latest_message) VALUES (%s, %s, %s, %s, %s)",
        (
            data["username"],
            uuid_from_time(
                datetime.fromtimestamp(data["created_at"]).replace(tzinfo=timezone.utc)
            )
            if data.get("created_at")
            else uuid_from_time(datetime.utcnow().replace(tzinfo=timezone.utc)),
            uuid.UUID(data["chat_id"]),
            data["name"],
            data["message"],
        ),
    )
    return future


@async_
def delete_users_latest_chat(scylladb, data):
    future = scylladb.execute_async(
        "DELETE FROM chats_by_user WHERE chat_id=%s AND username=%s AND latest_message_sent_at < %s",
        (
            uuid.UUID(data["chat_id"]),
            data["username"],
            uuid_from_time(
                datetime.fromtimestamp(data["created_at"]).replace(tzinfo=timezone.utc)
            ),
        ),
    )
    return future


@async_
def get_messages_list(scylladb, chat_id):
    future = scylladb.execute_async(
        "SELECT * FROM messages WHERE chat_id = %s ORDER BY created_at",
        (uuid.UUID(chat_id),),
    )
    return future


@async_
def get_chat_members(scylladb, chat_id):
    future = scylladb.execute_async(
        "SELECT members FROM chat_members WHERE chat_id = %s",
        (uuid.UUID(chat_id),),
    )
    return future


def get_init_chat_name(username, members):
    return ", ".join(filter(lambda name: name != username, members))


async def handle_send_message(scylladb, data):
    # TODO: use batch query
    chat_id = data["chat_id"]
    if not chat_id:
        initial = True
        chat_id = str(uuid.uuid1())
        data["chat_id"] = chat_id
        members = data["members"]
        await create_chat_members(scylladb, data)
    else:
        initial = False
        members_result: ResultSet = await get_chat_members(scylladb, chat_id)
        members = members_result.one()[0]
    async with anyio.create_task_group() as nursery:
        nursery.start_soon(create_message, scylladb, data)
        for member in members:
            data = {**data, "username": member}
            if initial:
                data["name"] = get_init_chat_name(member, members)
            else:
                latest_users_chat_result = await get_users_latest_chat(scylladb, data)
                latest_users_chat = latest_users_chat_result.one()
                data["name"] = latest_users_chat.name
            nursery.start_soon(delete_users_latest_chat, scylladb, data)
            nursery.start_soon(create_users_latest_chat, scylladb, data)
    return {"chat_id": chat_id}
