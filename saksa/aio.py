import asyncio
from functools import wraps

import trio


def trio_to_asyncio(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        asyncio_loop = asyncio.get_running_loop()

        def run_sync_soon_threadsafe(fn):
            asyncio_loop.call_soon_threadsafe(fn)

        # Revised 'done' callback: set a Future
        done_fut = asyncio_loop.create_future()
        def done_callback(trio_main_outcome):
            done_fut.set_result(trio_main_outcome)

        trio.lowlevel.start_guest_run(
            f,
            *args,
            *kwargs.values(),
            run_sync_soon_threadsafe=run_sync_soon_threadsafe,
            done_callback=done_callback,
            host_uses_signal_set_wakeup_fd=True,
        )

        # Wait for the guest run to finish
        trio_main_outcome = await done_fut
        # Pass through the return value or exception from the guest run
        return trio_main_outcome.unwrap()

    return wrapper


def async_(f):
    @wraps(f)
    @trio_to_asyncio
    async def wrapper(*args, **kwargs):
        fut = f(*args, **kwargs)

        result = await trio.to_thread.run_sync(fut.result)
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
