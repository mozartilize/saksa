import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { io } from "socket.io-client";

import store from "../store";
import { messagesApi } from "./messages";
import { triggerNewMessageEvent } from '../features/chatlist';
import { removeSentMsgIdentifier } from '../features/chatbox';

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
              dispatch(
                messagesApi.util.updateQueryData('fetchMessages', state.selectingChat.value.chat_id, (draft) => {
                  draft.push(message);
                })
              )
              dispatch(triggerNewMessageEvent(message.created_at));
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
