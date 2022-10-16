import { Fragment, useEffect } from "react";
import { useSelector } from "react-redux";

import MessageComponent from "./MessageComponent";
import { useFetchMessagesQuery } from "./api/messages";

export default function MessagesComponent(props) {
  const selectingChat = useSelector((state) => state.selectingChat.value);
  const newMessageTimestampWS = useSelector(
    (state) => state.newMessageTimestampWS.value
  );

  const { data, isLoading } = useFetchMessagesQuery(selectingChat ? selectingChat.chat_id : null, {
    skip: selectingChat === null || (selectingChat && !selectingChat.chat_id),
  });

  useEffect(() => {
    if (
      !isLoading &&
      data &&
      data.length > 0
    ) {
      props.root.scrollTop = props.root.scrollHeight;
    }
  });

  return isLoading || !data || (data && data.length === 0) ? (
    <Fragment></Fragment>
  ) : (
    data.map((message) => (
      <MessageComponent key={message.created_at} message={message} />
    ))
  );
}
