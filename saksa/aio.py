import asyncio
from functools import wraps

import anyio


def async_(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        fut = f(*args, **kwargs)

        result = await anyio.to_thread.run_sync(fut.result)
        return result

    return wrapper
