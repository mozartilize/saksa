import { createSlice, configureStore } from '@reduxjs/toolkit'

export const chatMessages = createSlice({
  name: 'chatMessages',
  initialState: {
    value: [],
  },
  reducers: {
    setMessages: (state, action) => {
      state.value = action.payload;
    },
    push: (state, action) => {
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
    set: (state, action) => {
      state.value = action.payload;
    },
    empty: (state) => {
      state.value = "";
    }
  },
})

// Action creators are generated for each case reducer function
export const { push, setMessages } = chatMessages.actions
export const { set, empty } = inputMessage.actions

export default configureStore({
  reducer: {
    chatMessages: chatMessages.reducer,
    inputMessage: inputMessage.reducer,
  },
})