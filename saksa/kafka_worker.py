from uuid import UUID

import anyio
import faust
from cassandra.util import datetime_from_uuid1

from saksa.scylladb import ScyllaDB
from saksa.settings import settings
from saksa.message_service import get_chat_members


app = faust.App('saksa', broker=f'kafka://{settings.kafka_bootstrap_servers}', store='rocksdb://')

topic = app.topic('scylladb.saksa.messages')

scylladb = ScyllaDB(settings.SCYLLADB_SERVER)


async def _send_to_user_topic(topic, value):
    await topic.send(value=value)


@app.agent(topic)
async def forward_message_to_user_topic(stream):
    with scylladb.make_session("saksa") as scylla_session:
        async for value in stream:
            message_log = value['payload']['after']
            chat_id = message_log['chat_id']
            members_result = await get_chat_members(scylla_session, chat_id)
            members = members_result.one()[0]
            message = {
                "chat_id": message_log['chat_id'],
                "created_at": datetime_from_uuid1(UUID(message_log['created_at'])).timestamp(),
                "message": message_log['message']['value'],
                "sender": message_log['sender']['value'],
            }
            async with anyio.create_task_group() as tg:
                for member in members:
                    user_topic = app.topic(member)
                    tg.start_soon(_send_to_user_topic, user_topic, message)
