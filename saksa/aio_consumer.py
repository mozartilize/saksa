import trio
from confluent_kafka import Consumer


class AIOConsumer:
    def __init__(self, configs):
        self._consumer = Consumer(configs)
        self._cancelled = False
        self._timeout = 10

    def poll(self, send_to_trio):
        msg = self._consumer.poll(self._timeout)
        trio.from_thread.run(send_to_trio.send, msg)

    async def start(self):
        send_to_trio, receive_from_thread = trio.open_memory_channel(0)
        async with trio.open_nursery() as nursery:
            while not self._cancelled:
                nursery.start_soon(trio.from_thread.run_sync, self.poll, send_to_trio)
                msg = await receive_from_thread.receive()
                print(msg)

    def close(self):
        self._cancelled = True