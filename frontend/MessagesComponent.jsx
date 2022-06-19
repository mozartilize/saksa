import React, { useState, useEffect } from 'react';

import { SelectedChatIdCtx } from "./ctx";
import MessageComponent from "./MessageComponent";

export default function MessagesComponent(props) {
  const selectedChatId = React.useContext(SelectedChatIdCtx);

  const [messages, setMessages] = useState([]);

  useEffect(() => {
      async function fetchMessages() {
        const messagesResp = await fetch(`/api/v1/messages?chat_id=${selectedChatId}`);
        setMessages(await messagesResp.json());
      }
      fetchMessages();
      return () => {};
  }, [selectedChatId]);

  return (
    messages.map(message => <MessageComponent key={message.created_at} message={message.message}/>)
  );
}