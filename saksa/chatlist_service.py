from anyio import create_task_group

from .aio import async_

from .user_service import search_user


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
    for result in results:
        for chat in result.all()[::-1]:
            try:
                chatlist.append(
                    {
                        "chat_id": chat.chat_id,
                        "latest_message": chat.latest_message,
                        "latest_message_sent_at": chat.latest_message_sent_at,
                        "name": chat.name,
                    }
                )
            except AttributeError:
                chatlist.append(
                    {
                        "chat_id": None,
                        "latest_message": None,
                        "latest_message_sent_at": None,
                        "name": chat.username,
                    }
                )
    return chatlist
