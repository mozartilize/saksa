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


import time
from concurrent.futures import ThreadPoolExecutor


@async_
def foo():
    def _foo():
        time.sleep(1)
        return 10

    with ThreadPoolExecutor(max_workers=1) as exec:
        fut = exec.submit(_foo)
        return fut
