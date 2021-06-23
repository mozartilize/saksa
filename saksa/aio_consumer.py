import trio
from confluent_kafka import Consumer


class AIOConsumer:
    def __init__(self, configs):
        self._consumer = Consumer(configs)
        self._cancelled = False

    def _poll(self, send_to_trio, timeout):
        msg = self._consumer.poll(timeout)
        trio.from_thread.run(send_to_trio.send, msg)

    def subscribe(self, topics):
        self._consumer.subscribe(topics)

    async def _spawn_poll(self, send_to_trio, timeout):
        await trio.to_thread.run_sync(self._poll, send_to_trio, timeout, cancellable=True)

    async def poll(self, timeout, nursery):
        send_to_trio, receive_from_thread = trio.open_memory_channel(0)
        nursery.start_soon(self._spawn_poll, send_to_trio, timeout)
        msg = await receive_from_thread.receive()
        receive_from_thread.close()
        send_to_trio.close()
        return msg

    def close(self):
        self._consumer.close()
