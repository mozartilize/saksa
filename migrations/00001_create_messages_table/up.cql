CREATE TABLE messages (
    chat_id UUID,
    sender VARCHAR,
    message TEXT,
    created_at TIMEUUID,
    PRIMARY KEY (chat_id, created_at)
)
WITH CLUSTERING ORDER BY (created_at DESC);
