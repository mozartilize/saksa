-- select * from chats_by_user
-- where username = :somebody
-- order by latest_message_sent_at desc
----
-- delete from chats_by_user
-- where username = :somebody
-- and chat_id = :some_chat_id
-- and latest_message_sent_at < :some_time


CREATE TABLE chats_by_user (
    username VARCHAR,
    chat_id UUID,
    latest_message_sent_at TIMEUUID,
    latest_message TEXT,
    name VARCHAR,
    PRIMARY KEY (username, chat_id, latest_message_sent_at)
);
