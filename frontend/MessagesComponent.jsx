import { useEffect } from 'react';
import { useSelector } from 'react-redux';

import store from "./store";
import { setMessages } from './features/chatbox';
import MessageComponent from "./MessageComponent";

export default function MessagesComponent(props) {
  const selectingChatId = useSelector(state => state.selectingChatId.value);

  useEffect(() => {
    async function fetchMessages() {
      const messagesResp = await fetch(`/api/v1/messages?chat_id=${selectingChatId}`);
      store.dispatch(setMessages(await messagesResp.json()));
    };
    fetchMessages();
    return () => {}
  }, []);

  const messages = useSelector(state => state.chatMessages.value);

  return (
    messages.map(message => <MessageComponent key={message.created_at} message={message}/>)
  )
}
