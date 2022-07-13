import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const messagesApi = createApi({
  reducerPath: 'messagesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['Messages'],
  endpoints: builder => ({
    fetchMessages: builder.query({
      query: (selectingChatId) => `/messages?chat_id=${selectingChatId}`,
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
