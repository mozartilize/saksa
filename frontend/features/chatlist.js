import { createSlice } from "@reduxjs/toolkit";

export const chatList = createSlice({
  name: 'chatList',
  initialState: {
    value: [],
  },
  reducers: {
    setChatList: (state, action) => {
      state.value = action.payload;
    },
    addChat: (state, action) => {
      state.value.push(action.payload);
    },
  },
})

export const selectingChat = createSlice({
  name: 'selectingChat',
  initialState: {
    value: null,
  },
  reducers: {
    setChatNew: (state, action) => {
      state.value = action.payload;
    },
  },
})

export const searchChatQuery = createSlice({
  name: 'searchChatQuery',
  initialState: {
    value: "",
  },
  reducers: {
    setSearchChatQuery: (state, action) => {
      state.value = action.payload;
    },
  },
})

export const {setChatList, addChat} = chatList.actions;
export const {setChatNew} = selectingChat.actions;
export const {setSearchChatQuery} = searchChatQuery.actions;
