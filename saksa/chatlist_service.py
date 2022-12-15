import uuid

from anyio import create_task_group
from cassandra.cluster import ResultSet

from .aio import async_
from .user_service import search_user


@async_
def get_chat_members(scylladb, chat_id: str):
    future = scylladb.execute_async(
        "SELECT members FROM chat_members WHERE chat_id = %s",
        (uuid.UUID(chat_id),),
    )
    return future


@async_
def get_chatlist_for_user(scylladb, username, paginator_params, query_str=""):
    query = "SELECT * FROM chats_by_user WHERE username = %s AND latest_message_sent_at < %s"
    query_params = [username, paginator_params["cursor"]]
    if query_str:
        query += " AND name LIKE %s"
        query_params.append(f"%{query_str}%")
    query += " LIMIT %s ALLOW FILTERING"
    query_params.append(paginator_params["size"])
    future = scylladb.execute_async(query, query_params)
    return future


async def search_chatlist(scylladb, username, paginator_params, query_str=""):
    results = [None, None]

    async def run_one(i, async_fn, *args):
        results[i] = await async_fn(*args)

    tasks = [
        (get_chatlist_for_user, scylladb, username, paginator_params, query_str),
        (search_user, scylladb, query_str),
    ]
    async with create_task_group() as tg:
        for i, task in enumerate(tasks):
            async_fn, *args = task
            tg.start_soon(run_one, i, async_fn, *args)
    chatlist = []
    chatlist_members_map = {}
    for result in results:
        for chat in result.all():
            try:
                members_result: ResultSet = await get_chat_members(scylladb, str(chat.chat_id))
                members = members_result.one()[0]
                chatlist_members_map[tuple(sorted(members))] = 1
                chatlist.append(
                    {
                        "chat_id": chat.chat_id,
                        "latest_message": chat.latest_message,
                        "latest_message_sent_at": chat.latest_message_sent_at,
                        "name": chat.name,
                        "search": False,
                    }
                )
            except AttributeError as e:
                if not chatlist_members_map.get(tuple(sorted([username, chat.username]))):
                    chatlist.append(
                        {
                            "chat_id": uuid.uuid1(),
                            "latest_message": None,
                            "latest_message_sent_at": None,
                            "name": chat.username,
                            "search": True,
                        }
                    )
    return chatlist
