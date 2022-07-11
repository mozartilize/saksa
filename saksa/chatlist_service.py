from .aio import async_


@async_
def get_chatlist_for_user(scylladb, username):
    future = scylladb.execute_async(
        "SELECT * FROM chats_by_user WHERE username = %s",
        (username,),
    )
    return future
