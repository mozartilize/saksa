import { useSelector, useDispatch } from 'react-redux';

import MessageComponent from "./MessageComponent";

export default function MessagesComponent(props) {
  const messages = useSelector(state => state.chatMessages.value);
  return (
    messages.map(message => <MessageComponent key={message.created_at} message={message.message}/>)
  )
}