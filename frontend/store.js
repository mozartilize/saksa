import { configureStore } from '@reduxjs/toolkit';

import {chatMessages, inputMessage} from "./features/chatbox";
import {currentUser} from "./features/auth";
import {chatList, selectingChatId, newMessageTimestamp} from "./features/chatlist";

import { messagesApi } from './api/messages'
import { chatListApi } from './api/chatlist'


export default configureStore({
  reducer: {
    chatMessages: chatMessages.reducer,
    inputMessage: inputMessage.reducer,
    currentUser: currentUser.reducer,
    chatList: chatList.reducer,
    selectingChatId: selectingChatId.reducer,
    newMessageTimestamp: newMessageTimestamp.reducer,
    [messagesApi.reducerPath]: messagesApi.reducer,
    [chatListApi.reducerPath]: chatListApi.reducer,
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware().concat(messagesApi.middleware)
})
