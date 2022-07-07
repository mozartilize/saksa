import { Fragment, useEffect } from 'react';
import { useSelector } from 'react-redux';

import MessageComponent from "./MessageComponent";
import { useFetchMessagesQuery } from './api/messages'
import { on, off } from "./events";

export default function MessagesComponent(props) {
  const selectingChatId = useSelector(state => state.selectingChatId.value);
  const newMessageTimestamp = useSelector(state => state.newMessageTimestamp.value);

  const { data, isLoading } = useFetchMessagesQuery(selectingChatId);

  useEffect(() => {
    if (!isLoading && data[data.length-1].created_at == newMessageTimestamp) {
      props.root.scrollTop = props.root.scrollHeight;
    }
  }, [data, newMessageTimestamp]);

  return (
    isLoading ? <Fragment></Fragment> : data.map(message => <MessageComponent key={message.created_at} message={message}/>)
  )
}
