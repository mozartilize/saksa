import { Fragment, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import classNames from "classnames";
import { useFetchChatListQuery } from "./api/chatlist";
import { messagesApi } from "./api/messages";

import { setChatNew, setSearchChatQuery } from "./features/chatlist";

function ChatComponent(props) {
  const selectingChat = useSelector((state) => state.selectingChat.value);
  const msOffset = new Date().getTimezoneOffset() * 60;
  const dispatch = useDispatch();

  function onSelectChat(e) {
    dispatch(setChatNew(props.chat));
  }

  return (
    <div
      className={classNames("chat", {
        selected: selectingChat && selectingChat.chat_id == props.chat.chat_id,
      })}
      onClick={onSelectChat}
    >
      <div>
        <b>{props.chat.name}</b>
      </div>
      <div>{props.chat.latest_message}</div>
      <div>
        <small>
          {new Date(
            (props.chat.latest_message_sent_at - msOffset) * 1000
          ).toLocaleString()}
        </small>
      </div>
    </div>
  );
}

export default function ChatListComponent(props) {
  const dispatch = useDispatch();

  const searchQuery = useSelector((state) => state.searchChatQuery.value);
  const currentUser = useSelector((state) => state.currentUser.value);

  const { data, isLoading } = useFetchChatListQuery({
    username: currentUser,
    searchQuery,
  });

  return (
    <Fragment>
      <div id="search-chat">
        <input
          id="search-chat-input"
          type="text"
          name="search_chat"
          value={searchQuery}
          onChange={(e) => dispatch(setSearchChatQuery(e.target.value))}
        />
      </div>
      {isLoading ? (
        <Fragment></Fragment>
      ) : (
        data.map((chat) => (
          <ChatComponent key={`${chat.chat_id}:${chat.name}`} chat={chat} />
        ))
      )}
    </Fragment>
  );
}
