import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const messagesApi = createApi({
  reducerPath: 'messagesApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1' }),
  endpoints: builder => ({
    fetchMessages: builder.query({
      query: (selectingChatId) => `/messages?chat_id=${selectingChatId}`,
    })
  })
})

export const { useFetchMessagesQuery } = messagesApi
