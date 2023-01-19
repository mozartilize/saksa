import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { io } from "socket.io-client";

import store from "../store";
import { messagesApi } from "./messages";
import { chatListApi } from "./chatlist";
import { pushMsg, removeSentMsgIdentifier } from '../features/chatbox';

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['auth'],
  endpoints: builder => ({
    verifyUser: builder.query({
      query: () => "/auth/verify",
      async onCacheEntryAdded(
        arg,
        { cacheDataLoaded, cacheEntryRemoved, dispatch }
      ) {
        // create a websocket connection when the cache subscription starts
        const state = store.getState();
        const ws = io("/", {auth: {username: state.currentUser.value}, transports: ["websocket"]});
        try {
          // wait for the initial query to resolve before proceeding
          await cacheDataLoaded;

          // when data is received from the socket connection to the server,
          // if it is a message and for the appropriate channel,
          // update our query result with the received message
          ws.on("connect", (arg) => {
            console.log("I'm connected");
          });
          ws.on("message", (bin_data) => {
            const state = store.getState();
            const buffer = new Uint8Array(bin_data);
            const fileString= new TextDecoder().decode(buffer);
            const message = JSON.parse(fileString);
            console.log(message);
            if (!state.sentMsgIdentifiers.value[`${message.chat_id}:${message.created_at}`]) {
              if (state.selectingChat.value && state.selectingChat.value.chat_id == message.chat_id) {
                dispatch(pushMsg(message));
              }
              dispatch(
                chatListApi.util.updateQueryData(
                  'fetchChatList',
                  {username: state.currentUser.value, searchQuery: ""},
                  (draft) => {
                    const chatIndex = draft.map(chat => chat.chat_id).indexOf(message.chat_id);
                    if (chatIndex < 0) {
                      dispatch(chatListApi.util.invalidateTags(["ChatList"]));
                    } else {
                      const chat = draft.splice(chatIndex, 1)[0];
                      chat.latest_message = message.message;
                      chat.latest_message_sent_at = message.created_at;
                      draft.unshift(chat);
                    }
                  }
                )
              );
            }
            else {
              dispatch(removeSentMsgIdentifier(`${message.chat_id}:${message.created_at}`));
            }
          });
        } catch {
          // no-op in case `cacheEntryRemoved` resolves before `cacheDataLoaded`,
          // in which case `cacheDataLoaded` will throw
        }
        // cacheEntryRemoved will resolve when the cache subscription is no longer active
        await cacheEntryRemoved;
        // perform cleanup steps once the `cacheEntryRemoved` promise resolves
        ws.disconnect();
      },
    }),
  })
})

export const { useVerifyUserQuery } = authApi
