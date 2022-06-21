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

export const selectingChatId = createSlice({
  name: 'selectingChatId',
  initialState: {
    value: "f8680106-a790-4b6e-912f-7adb93f2a69a",
  },
  reducers: {
    setChat: (state, action) => {
      state.value = action.payload;
    },
  },
})

export const {setChatList, addChat} = chatList.actions;
export const {setChat} = selectingChatId.actions;