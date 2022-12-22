import { configureStore } from "@reduxjs/toolkit";

import {
  chatMessages,
  inputMessage,
  sentMsgIdentifiers,
  sidePaneState,
} from "./features/chatbox";
import { currentUser } from "./features/auth";
import { chatList, selectingChat, searchChatQuery } from "./features/chatlist";

import { messagesApi } from "./api/messages";
import { chatListApi } from "./api/chatlist";
import { authApi } from "./api/auth";

export default configureStore({
  reducer: {
    chatMessages: chatMessages.reducer,
    inputMessage: inputMessage.reducer,
    sentMsgIdentifiers: sentMsgIdentifiers.reducer,
    currentUser: currentUser.reducer,
    chatList: chatList.reducer,
    selectingChat: selectingChat.reducer,
    searchChatQuery: searchChatQuery.reducer,
    sidePaneState: sidePaneState.reducer,
    [authApi.reducerPath]: authApi.reducer,
    [messagesApi.reducerPath]: messagesApi.reducer,
    [chatListApi.reducerPath]: chatListApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      messagesApi.middleware,
      chatListApi.middleware,
      authApi.middleware
    ),
});
