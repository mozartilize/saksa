import { Fragment } from "react";
import { useSelector, useDispatch } from "react-redux";

import { setInputMsg, emptyInputMsg, pushMsg } from "./features/chatbox";

export default function MessageInput(props) {
  const inputMessage = useSelector(state => state.inputMessage.value);
  const currentUser = useSelector(state => state.currentUser.value);
  const dispatch = useDispatch()

  return (
    <Fragment>
      <textarea name="" id="" cols="30" rows="5" value={inputMessage} onChange={(event) => dispatch(setInputMsg(event.target.value))}></textarea>
      <button onClick={() => { dispatch(pushMsg({sender: currentUser, message: inputMessage, created_at: (new Date()).getTime()}));  dispatch(emptyInputMsg())} }>Send</button>
    </Fragment>
  )
}
