import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';

import store from './store';

import { authApi, useVerifyUserQuery } from "./api/auth";

import MessagesComponent from './MessagesComponent';
import MessageInput from './MessageInput';
import ChatListComponent from './ChatListComponent';

import './index.css'

store.dispatch(authApi.endpoints.verifyUser.initiate());

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

const chatListEl = ReactDOM.createRoot(document.getElementById('chatlist'));
chatListEl.render(
  <Provider store={store}>
    <ChatListComponent />
  </Provider>
);
