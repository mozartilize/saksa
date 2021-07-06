#!/usr/bin/env python

import trio

from saksa.aio_consumer import AIOConsumer


async def main():
    c = AIOConsumer(
        {
            "bootstrap.servers": "127.0.0.1",
            "group.id": "mygroup",
            "auto.offset.reset": "largest",
        }
    )
    c.subscribe(["mytopic"])

    def close_consumer(c):
        print("closing...")
        c.close()

    # atexit.register(close_consumer, c)

    async with trio.open_nursery() as n:
        while True:
            try:
                msg = await c.poll(1.0, n)
                if not msg:
                    print("hmm")
                    continue
                if msg.error():
                    raise Exception("Message error")
                print(msg.value())
            except KeyboardInterrupt:
                close_consumer(c)
                raise


if __name__ == "__main__":
    trio.run(main)
