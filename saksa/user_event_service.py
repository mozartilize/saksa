import asyncio
import functools

from .aio_consumer import AIOConsumer, ConsumerExecutor
from .processors import EmitComsumedMessage
from .settings import settings


def handle_consume_events_done(done_fut: asyncio.Future, result_fut: asyncio.Future):
    try:
        done_fut.set_result(result_fut.result())
    except Exception as e:
        done_fut.set_exception(e)


async def consume_user_events(sio, sid, topic):
    c = AIOConsumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": sid,
            "auto.offset.reset": "largest",
        }
    )
    await c.subscribe([topic])
    consumer_exec = ConsumerExecutor(sid, c)
    consumer_exec.add_handler(EmitComsumedMessage(sio, sid))
    t = asyncio.create_task(consumer_exec.run_v2())
    # ensure that the polling task is working without error,
    # otherwise exception will be raised through `done_fut`
    # and connect handsake will fail
    done_fut = asyncio.Future()
    done_callback = functools.partial(handle_consume_events_done, done_fut)
    t.add_done_callback(done_callback)
    await asyncio.wait({done_fut}, timeout=0.5)
    t.remove_done_callback(done_callback)
    # TODO: shoule we only return the task and
    # consumer exector cancelled on task cancelled?
    return t, consumer_exec
