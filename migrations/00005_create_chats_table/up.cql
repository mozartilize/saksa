CREATE TABLE chats (
    username VARCHAR,
    chat_id UUID,
    name VARCHAR,
    latest_message_sent_at TIMEUUID,
    PRIMARY KEY (username, chat_id)
);
