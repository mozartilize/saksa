from ..aio import async_


@async_
def create_user(scylladb, username):
    fut = scylladb.execute_async(
        "INSERT INTO users(username) VALUES(%s) IF NOT EXISTS", [username]
    )
    return fut
