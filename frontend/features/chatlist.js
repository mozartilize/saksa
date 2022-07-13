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
    value: null,
  },
  reducers: {
    setChat: (state, action) => {
      state.value = action.payload;
    },
  },
})

export const newMessageTimestampWS = createSlice({
  name: 'newMessageTimestampWS',
  initialState: {
    value: 0,
  },
  reducers: {
    triggerNewMessageEvent: (state, action) => {
      state.value = action.payload;
    }
  },
})

export const {setChatList, addChat} = chatList.actions;
export const {setChat} = selectingChatId.actions;
export const {triggerNewMessageEvent} = newMessageTimestampWS.actions;
