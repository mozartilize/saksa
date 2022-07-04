import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { io } from "socket.io-client";

import store from "../store";

export const messagesApi = createApi({
  reducerPath: 'messagesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['Messages'],
  endpoints: builder => ({
    fetchMessages: builder.query({
      query: (selectingChatId) => `/messages?chat_id=${selectingChatId}`,
      async onCacheEntryAdded(
        arg,
        { updateCachedData, cacheDataLoaded, cacheEntryRemoved }
      ) {
        // create a websocket connection when the cache subscription starts
        const state = store.getState();
        const ws = io("/", {auth: {username: state.currentUser.value}, transports: ["websocket"]});
        try {
          // wait for the initial query to resolve before proceeding
          await cacheDataLoaded

          // // when data is received from the socket connection to the server,
          // // if it is a message and for the appropriate channel,
          // // update our query result with the received message
          // const listener = (event) => {
          //   const data = JSON.parse(event.data)
          //   if (!isMessage(data) || data.channel !== arg) return

          //   updateCachedData((draft) => {
          //     draft.push(data)
          //   })
          // }
          ws.on("connect", (arg) => {
            console.log("I'm connected");
          });
          ws.on("message", (data) => {
            const buffer = new Uint8Array(data);
            const fileString= String.fromCharCode.apply(null, buffer);
            console.log(fileString);
            // const message = JSON.parse(fileString);
          });
        } catch {
          // no-op in case `cacheEntryRemoved` resolves before `cacheDataLoaded`,
          // in which case `cacheDataLoaded` will throw
        }
        // cacheEntryRemoved will resolve when the cache subscription is no longer active
        await cacheEntryRemoved
        // perform cleanup steps once the `cacheEntryRemoved` promise resolves
        ws.disconnect()
      },
    }),
    sendMessage: builder.mutation({
      query: (messageFormData) => ({
        url: `/messages`,
        method: "post",
        body: messageFormData,
      }),
      onQueryStarted: async (messageFormData, { dispatch, queryFulfilled }) => {
        const selectingChatId = messageFormData["chat_id"];
        const patchResult = dispatch(
          messagesApi.util.updateQueryData('fetchMessages', selectingChatId, (draft) => {
            draft.push(messageFormData);
          })
        )
        try {
          await queryFulfilled
        } catch {
          // patchResult.undo();
        }
      },
    }),
  })
})

export const { useFetchMessagesQuery, useSendMessageMutation } = messagesApi
