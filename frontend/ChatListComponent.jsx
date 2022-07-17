import { Fragment, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useFetchChatListQuery, chatListApi } from "./api/chatlist";
import { messagesApi } from "./api/messages";

import { setChatNew } from "./features/chatlist";

function ChatComponent(props) {
  const msOffset = new Date().getTimezoneOffset() * 60;
  const dispatch = useDispatch();

  function onSelectChat(e) {
    dispatch(setChatNew(props.chat));
    if (!props.chat.chat_id) {
      dispatch(messagesApi.util.updateQueryData("fetchMessages", undefined, (tempMessages) => {
        Object.assign(tempMessages, [])
      }))
    }
  }

  return (
    <div className="chat" onClick={onSelectChat}>
      <div><b>{props.chat.name}</b></div>
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
  const [searchQuery, setSearchQuery] = useState("")
  console.log(searchQuery);
  const currentUser = useSelector((state) => state.currentUser.value);

  const { data, isLoading } = useFetchChatListQuery({username: currentUser, searchQuery});

  return (
    <Fragment>
      <div id="search-chat">
        <input type="text" onChange={(e)=>setSearchQuery(e.target.value)} name="search_chat" value={searchQuery} id="search-chat-input" />
      </div>
      {isLoading ? (
        <Fragment></Fragment>
      ) : (
        data.map((chat) => <ChatComponent key={`${chat.chat_id}:${chat.name}`} chat={chat} />)
      )}
    </Fragment>
  );
}
