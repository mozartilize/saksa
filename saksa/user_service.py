from .aio import async_


@async_
def search_user(scylladb, query_str=""):
    query = "SELECT * FROM users WHERE username = null"
    query_params = []
    if query_str:
        query = "SELECT * FROM users WHERE username LIKE %s ALLOW FILTERING"
        query_params = [f"%{query_str}%"]
    future = scylladb.execute_async(query, query_params)
    return future
