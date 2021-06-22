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

    async def poll(self, timeout):
        send_to_trio, receive_from_thread = trio.open_memory_channel(0)
        async with trio.open_nursery() as nursery:
            while not self._cancelled:
                nursery.start_soon(trio.to_thread.run_sync, self._poll, send_to_trio, timeout)
                msg = await receive_from_thread.receive()
                if msg is None:
                    continue
                if msg.error():
                    print("Consumer error: {}".format(msg.error()))
                    continue

                print('Received message: {}'.format(msg.value().decode('utf-8')))

    def close(self):
        self._cancelled = True