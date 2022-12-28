import asyncio

import anyio


async def foo():
    print("hello")
    asyncio.sleep(1)
    await anyio.sleep(1)
