import { Fragment } from "react";
import { useSelector, useDispatch } from "react-redux";

import { setInputMsg, emptyInputMsg } from "./features/chatbox";
import { useSendMessageMutation } from "./api/messages";

export default function MessageInput(props) {
  const dispatch = useDispatch();
  const selectingChatId = useSelector(state => state.selectingChatId.value);
  const inputMessage = useSelector(state => state.inputMessage.value);
  const currentUser = useSelector(state => state.currentUser.value);
  const [sendMessage, { isLoading }] = useSendMessageMutation();

  async function handleSendMessage() {
    await sendMessage({
      chat_id: selectingChatId,
      created_at: new Date().getTime() / 1000 + new Date().getTimezoneOffset() * 60,
      message: inputMessage,
      sender: currentUser,
    }).unwrap();
    dispatch(emptyInputMsg());
  }

  return (
    <Fragment>
      <textarea name="" id="" cols="30" rows="5" value={inputMessage} onChange={(event) => dispatch(setInputMsg(event.target.value))}></textarea>
      <button onClick={handleSendMessage} disabled={isLoading}>Send</button>
    </Fragment>
  )
}
