import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const chatListApi = createApi({
  reducerPath: 'chatlistApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  tagTypes: ['ChatList'],
  endpoints: builder => ({
    fetchChatList: builder.query({
      query: ({username, searchQuery}) => searchQuery!=="" ? `/chat?username=${username}&s=${searchQuery}`: `/chat?username=${username}`,
    }),
  })
})

export const { useFetchChatListQuery, useAddChatMutation } = chatListApi
