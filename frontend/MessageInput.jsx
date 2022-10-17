import { Fragment } from "react";
import { useSelector, useDispatch } from "react-redux";

import { setInputMsg, emptyInputMsg, pushSentMsgIdentifier } from "./features/chatbox";
import { useSendMessageMutation } from "./api/messages";
import { chatListApi } from "./api/chatlist";

export default function MessageInput(props) {
  const dispatch = useDispatch();
  const selectingChat = useSelector((state) => state.selectingChat.value);
  const inputMessage = useSelector((state) => state.inputMessage.value);
  const currentUser = useSelector((state) => state.currentUser.value);
  const [sendMessage, { isLoading }] = useSendMessageMutation();

  async function handleSendMessage() {
    const msg = {
      chat_id: selectingChat.chat_id,
      created_at:
        new Date().getTime() / 1000 + new Date().getTimezoneOffset() * 60,
      message: inputMessage,
      sender: currentUser,
    };
    if (!selectingChat.chat_id) {
      msg.members = [currentUser, selectingChat.name];
    }
    await sendMessage(msg).unwrap();
    dispatch(emptyInputMsg());
    dispatch(
      chatListApi.util.updateQueryData(
        'fetchChatList',
        {username: currentUser, searchQuery: ""},
        (draft) => {
          const chatIndex = draft.map(chat => chat.chat_id).indexOf(msg.chat_id);
          const chat = draft.splice(chatIndex, 1)[0];
          chat.latest_message = msg.message;
          chat.latest_message_sent_at = msg.created_at;
          draft.unshift(chat);
        }
      )
    );
    if (selectingChat.chat_id) {
      dispatch(pushSentMsgIdentifier(`${selectingChat.chat_id}:${msg.created_at}`));
    }
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
