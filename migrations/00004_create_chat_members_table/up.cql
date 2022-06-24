CREATE TABLE chat_members (
    chat_id UUID PRIMARY KEY,
    members SET<VARCHAR>,
);
