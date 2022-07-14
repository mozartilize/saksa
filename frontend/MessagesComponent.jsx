import { Fragment, useEffect } from "react";
import { useSelector } from "react-redux";

import MessageComponent from "./MessageComponent";
import { useFetchMessagesQuery } from "./api/messages";

export default function MessagesComponent(props) {
  const selectingChatId = useSelector((state) => state.selectingChatId.value);
  const newMessageTimestampWS = useSelector(
    (state) => state.newMessageTimestampWS.value
  );

  const { data, isLoading } = useFetchMessagesQuery(selectingChatId, {
    skip: selectingChatId === null,
  });

  useEffect(() => {
    if (
      !isLoading &&
      data &&
      data.length > 0 &&
      data[data.length - 1].created_at == newMessageTimestampWS
    ) {
      props.root.scrollTop = props.root.scrollHeight;
    }
  }, [newMessageTimestampWS]);

  return isLoading || !data || (data && data.length === 0) ? (
    <Fragment></Fragment>
  ) : (
    data.map((message) => (
      <MessageComponent key={message.created_at} message={message} />
    ))
  );
}
