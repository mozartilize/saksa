CREATE TABLE chats_by_user (
    username VARCHAR,
    latest_message_sent_at TIMEUUID,
    chat_id UUID,
    latest_message TEXT,
    PRIMARY KEY ((username, chat_id), latest_message_sent_at)
)
WITH CLUSTERING ORDER BY (latest_message_sent_at DESC);
