import { Fragment } from 'react';
import { useSelector } from 'react-redux';

import MessageComponent from "./MessageComponent";
import { useFetchMessagesQuery } from './api/messages'

export default function MessagesComponent(props) {
  const selectingChatId = useSelector(state => state.selectingChatId.value);

  const { data, isLoading } = useFetchMessagesQuery(selectingChatId);

  return (
    isLoading ? <Fragment></Fragment> : data.map(message => <MessageComponent key={message.created_at} message={message}/>)
  )
}
