import { Fragment } from "react";
import { useSelector, useDispatch } from "react-redux";

import {set, push, empty} from "./store";

export default function MessageInput(props) {
  const inputMessage = useSelector(state => state.inputMessage.value);
  const dispatch = useDispatch()

  return (
    <Fragment>
      <textarea name="" id="" cols="30" rows="5" value={inputMessage} onChange={(event) => dispatch(set(event.target.value))}></textarea>
      <button onClick={() => { dispatch(push({message: inputMessage, created_at: (new Date()).getTime()}));  dispatch(empty())} }>Send</button>
    </Fragment>
  )
}