import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import store from './store';

import MessagesComponent from './MessagesComponent';
import MessageInput from './MessageInput';

import './index.css'

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
