import anyio
import faust

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
            chat_id = value['payload']['after']['chat_id']
            members_result = await get_chat_members(scylla_session, chat_id)
            members = members_result.one()[0]
            async with anyio.create_task_group() as tg:
                for member in members:
                    user_topic = app.topic(member)
                    tg.start_soon(_send_to_user_topic, user_topic, value['payload']['after'])
