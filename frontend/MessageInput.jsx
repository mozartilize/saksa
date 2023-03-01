import React, { Fragment } from "react";
import { useSelector, useDispatch } from "react-redux";

import {
  setInputMsg,
  emptyInputMsg,
} from "./features/chatbox";
import { useSendMessageMutation } from "./api/messages";
import { chatListApi } from "./api/chatlist";

export default function MessageInput() {
  const dispatch = useDispatch();
  const selectingChat = useSelector((state) => state.selectingChat.value);
  const inputMessage = useSelector((state) => state.inputMessage.value);
  const currentUser = useSelector((state) => state.currentUser.value);
  const [sendMessage, { isLoading }] = useSendMessageMutation();
  const searchQuery = useSelector((state) => state.searchChatQuery.value);

  async function handleSendMessage() {
    const msg = {
      chat_id: selectingChat.search ? null : selectingChat.chat_id,
      created_at:
        new Date().getTime() / 1000 + new Date().getTimezoneOffset() * 60,
      message: inputMessage,
      sender: currentUser,
    };
    if (selectingChat.search) {
      msg.members = [currentUser, selectingChat.name];
    }
    dispatch(emptyInputMsg());
    const sendMessageResp = await sendMessage(msg).unwrap();
    dispatch(
      chatListApi.util.updateQueryData(
        "fetchChatList",
        { username: currentUser, searchQuery: searchQuery },
        (draft) => {
          const chatIndex = draft
            .map((chat) => chat.chat_id)
            .indexOf(msg.chat_id);
          const chat = draft.splice(chatIndex, 1)[0];
          chat.chat_id = sendMessageResp.data.chat_id;
          chat.latest_message = msg.message;
          chat.latest_message_sent_at = msg.created_at;
          draft.unshift(chat);
        }
      )
    );
    dispatch(chatListApi.util.invalidateTags(["ChatList"]));
  }

  function onEnterPress(e) {
    if (e.keyCode == 13 && e.shiftKey == false) {
      handleSendMessage();
      e.preventDefault();
    }
  }

  return selectingChat ? (
    <Fragment>
      <textarea
        name=""
        id=""
        cols="30"
        rows="5"
        value={inputMessage}
        onChange={(event) => dispatch(setInputMsg(event.target.value))}
        onKeyDown={onEnterPress}
      ></textarea>
      <button onClick={handleSendMessage} disabled={isLoading}>
        Send
      </button>
    </Fragment>
  ) : (
    <Fragment></Fragment>
  );
}
