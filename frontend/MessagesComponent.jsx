import { Fragment, useEffect } from 'react';
import { useSelector } from 'react-redux';

import MessageComponent from "./MessageComponent";
import { useFetchMessagesQuery } from './api/messages'

export default function MessagesComponent(props) {
  const selectingChatId = useSelector(state => state.selectingChatId.value);
  const newMessageTimestampWS = useSelector(state => state.newMessageTimestampWS.value);

  let data = [];
  let isLoading = false;
  if (selectingChatId) {
    const result = useFetchMessagesQuery(selectingChatId);
    data = result.data;
    isLoading = result.isLoading;
  }

  useEffect(() => {
    if (!isLoading && data.length > 0 && data[data.length-1].created_at == newMessageTimestampWS) {
      props.root.scrollTop = props.root.scrollHeight;
    }
  }, [data, newMessageTimestampWS]);

  return (
    (isLoading || (data && data.length === 0)) ? <Fragment></Fragment> : data.map(message => <MessageComponent key={message.created_at} message={message}/>)
  )
}
