import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";

import store from "./store";

import MessagesComponent from "./MessagesComponent";
import MessageInput from "./MessageInput";
import ChatListComponent from "./ChatListComponent";
import UserComponent from "./UserComponent";
import ChatInfoComponent from "./ChatInfoComponent";

import "./index.css";

const messegesEl = document.getElementById("messages");
const messagesNode = ReactDOM.createRoot(messegesEl);
messagesNode.render(
  <Provider store={store}>
    <MessagesComponent root={messegesEl} />
  </Provider>
);

const messegeInputNode = ReactDOM.createRoot(
  document.getElementById("message-input")
);
messegeInputNode.render(
  <Provider store={store}>
    <MessageInput />
  </Provider>
);

const chatListNode = ReactDOM.createRoot(document.getElementById("chatlist"));
chatListNode.render(
  <Provider store={store}>
    <ChatListComponent />
  </Provider>
);

const userNode = ReactDOM.createRoot(document.getElementById("user"));
userNode.render(
  <Provider store={store}>
    <UserComponent />
  </Provider>
);

const chatInfoNode = ReactDOM.createRoot(document.getElementById("chat-info"));
chatInfoNode.render(
  <Provider store={store}>
    <ChatInfoComponent />
  </Provider>
);
