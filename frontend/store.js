import { configureStore } from '@reduxjs/toolkit';

import {chatMessages, inputMessage} from "./features/chatbox";
import {currentUser} from "./features/auth";
import {chatList, selectingChatId} from "./features/chatlist";

export default configureStore({
  reducer: {
    chatMessages: chatMessages.reducer,
    inputMessage: inputMessage.reducer,
    currentUser: currentUser.reducer,
    chatList: chatList.reducer,
    selectingChatId: selectingChatId.reducer,
  },
})
