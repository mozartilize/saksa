import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import store, {setMessages} from './store';

import MessagesComponent from './MessagesComponent';
import MessageInput from './MessageInput';

import './index.css'

const selectedChatId = "f8680106-a790-4b6e-912f-7adb93f2a69a";
const messagesResp = await fetch(`/api/v1/messages?chat_id=${selectedChatId}`);
store.dispatch(setMessages(await messagesResp.json()));

const messegesEl = ReactDOM.createRoot(document.getElementById('messages'));
messegesEl.render(
  <Provider store={store}>
    <MessagesComponent/>
  </Provider>
);

const messegeInputEl = ReactDOM.createRoot(document.getElementById('message-input'));
messegeInputEl.render(
  <Provider store={store}>
    <MessageInput />
  </Provider>
);