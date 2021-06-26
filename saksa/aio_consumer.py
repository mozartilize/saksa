import inspect

import trio
from confluent_kafka import Consumer


class AIOConsumer:
    def __init__(self, configs):
        self._consumer = Consumer(configs)

    def _poll(self, send_to_trio, timeout):
        msg = self._consumer.poll(timeout)
        trio.from_thread.run(send_to_trio.send, msg)

    async def subscribe(self, topics):
        await trio.to_thread.run_sync(self._consumer.subscribe, topics)

    async def _spawn_poll(self, send_to_trio, timeout):
        await trio.to_thread.run_sync(
            self._poll, send_to_trio, timeout, cancellable=True
        )

    async def poll(self, timeout, nursery):
        send_to_trio, receive_from_thread = trio.open_memory_channel(0)
        nursery.start_soon(self._spawn_poll, send_to_trio, timeout)
        msg = await receive_from_thread.receive()
        receive_from_thread.close()
        send_to_trio.close()
        return msg

    async def close(self):
        await trio.to_thread.run_sync(self._consumer.close)


class ConsumerExecutor:
    def __init__(self, sid: str, consumer: AIOConsumer):
        self._sid = sid
        self._consumer = consumer
        self._message_handlers = []
        self._stopped = trio.Event()

    def stop(self):
        self._stopped.set()

    def add_handler(self, handler):
        self._message_handlers.append(handler)

    async def run(self, nursery):
        while not self._stopped.is_set():
            print(f"{self._sid} polling...")
            msg = await self._consumer.poll(1.0, nursery)
            if not msg:
                continue
            nursery.start_soon(self._process_message, msg)
        await self._consumer.close()

    async def _process_message(self, msg):
        try:
            # open new nursery; if errors occur, it wont interrupt the main one
            async with trio.open_nursery() as nursery:
                for handler in self._message_handlers:
                    if inspect.iscoroutinefunction(handler.process):
                        nursery.start_soon(handler.process, msg)
                    else:
                        handler.process(msg)
        except Exception as e:
            print(e)
