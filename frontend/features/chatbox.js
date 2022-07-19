import { createSlice } from '@reduxjs/toolkit';

export const chatMessages = createSlice({
  name: 'chatMessages',
  initialState: {
    value: [],
  },
  reducers: {
    setMessages: (state, action) => {
      state.value = action.payload;
    },
    pushMsg: (state, action) => {
      state.value.push(action.payload);
    },
  },
})

export const inputMessage = createSlice({
  name: 'inputMessage',
  initialState: {
    value: "",
  },
  reducers: {
    setInputMsg: (state, action) => {
      state.value = action.payload;
    },
    emptyInputMsg: (state) => {
      state.value = "";
    }
  },
})

export const {setMessages, pushMsg} = chatMessages.actions;
export const {setInputMsg, emptyInputMsg} = inputMessage.actions;
