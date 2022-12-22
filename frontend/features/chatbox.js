import { createSlice } from "@reduxjs/toolkit";

export const chatMessages = createSlice({
  name: "chatMessages",
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
    prependMessages: (state, action) => {
      state.value = [...action.payload, ...state.value];
    },
  },
});

export const sentMsgIdentifiers = createSlice({
  name: "sentMsgIdentifiers",
  initialState: {
    value: {},
  },
  reducers: {
    pushSentMsgIdentifier: (state, action) => {
      state.value = { ...state.value, [action.payload]: true };
    },
    removeSentMsgIdentifier: (state, action) => {
      const { [action.payload]: val, ...others } = state.value;
      state.value = others;
    },
  },
});

export const inputMessage = createSlice({
  name: "inputMessage",
  initialState: {
    value: "",
  },
  reducers: {
    setInputMsg: (state, action) => {
      state.value = action.payload;
    },
    emptyInputMsg: (state) => {
      state.value = "";
    },
  },
});

export const sidePaneState = createSlice({
  name: "sidePaneState",
  initialState: {
    value: true,
  },
  reducers: {
    setSidePaneState: (state, action) => {
      state.value = action.payload;
    },
  },
});

export const { setMessages, pushMsg, prependMessages } = chatMessages.actions;
export const { setInputMsg, emptyInputMsg } = inputMessage.actions;
export const { setSidePaneState } = sidePaneState.actions;
export const { pushSentMsgIdentifier, removeSentMsgIdentifier } =
  sentMsgIdentifiers.actions;
