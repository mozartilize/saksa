import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { setChatNew } from '../features/chatlist';
import { pushMsg } from '../features/chatbox';


export const messagesApi = createApi({
  reducerPath: 'messagesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['Messages'],
  endpoints: builder => ({
    fetchMessages: builder.query({
      query: ({selectingChatId, cursor}) => `/messages?chat_id=${selectingChatId}&cursor=${cursor}`,
      transformResponse: responseData => {
        return responseData.data;
      },
    }),
    sendMessage: builder.mutation({
      query: (messageFormData) => ({
        url: `/messages`,
        method: "post",
        body: messageFormData,
      }),
      onQueryStarted: async (messageFormData, { dispatch, getState, queryFulfilled }) => {
        const selectingChatId = messageFormData["chat_id"];
        if (selectingChatId) {
          dispatch(pushMsg(messageFormData));
        }
        try {
          const {data: {data: data}} = await queryFulfilled;
          if (!selectingChatId) {
            const state = getState();
            const newChat = {
              chat_id: data["chat_id"],
              latest_message_sent_at: messageFormData["created_at"],
              latest_message: messageFormData["message"],
              name: state.selectingChat.value.name,
            }
            dispatch(setChatNew(newChat));
          }
        } catch {
          // patchResult.undo();
        }
      },
    }),
  })
})

export const { useFetchMessagesQuery, useSendMessageMutation } = messagesApi
