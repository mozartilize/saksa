import { Fragment } from 'react';
import { useSelector, useDispatch } from "react-redux";
import { useFetchChatListQuery } from "./api/chatlist";

import {setChat} from "./features/chatlist";

export function ChatComponent(props) {
  const msOffset = new Date().getTimezoneOffset() * 60;
  const dispatch = useDispatch();
  return (
    <div className="chat" onClick={() => dispatch(setChat(props.chat.chat_id))}>
      <div>
        {props.chat.chat_id.substring(0, 8)}
      </div>
      <div>
        {props.chat.latest_message}
      </div>
      <div>
        <small>{new Date((props.chat.latest_message_sent_at-msOffset)*1000).toLocaleString()}</small>
      </div>
    </div>
  )
}

export default function ChatListComponent(props) {
  const currentUser = useSelector(state => state.currentUser.value);

  const { data, isLoading } = useFetchChatListQuery(currentUser);
  return (
    isLoading ? <Fragment></Fragment> : data.map(chat => <ChatComponent key={chat.chat_id} chat={chat}/>)
  )
}
