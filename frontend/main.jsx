import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import store from './store';

import MessagesComponent from './MessagesComponent';
import MessageInput from './MessageInput';

import './index.css'

const messegesEl = document.getElementById('messages');
const messagesNode = ReactDOM.createRoot(messegesEl);
messagesNode.render(
  <Provider store={store}>
    <MessagesComponent root={messegesEl}/>
  </Provider>
);

const messegeInputNode = ReactDOM.createRoot(document.getElementById('message-input'));
messegeInputNode.render(
  <Provider store={store}>
    <MessageInput />
  </Provider>
);
