import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const chatListApi = createApi({
  reducerPath: 'chatlistApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['ChatList'],
  endpoints: builder => ({
    fetchChatList: builder.query({
      query: (username) => `/chat?username=${username}`,
    }),
    addChat: builder.mutation({
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

export const { useFetchChatListQuery, useAddChatMutation } = chatListApi
