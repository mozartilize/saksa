import { useEffect } from "react";
import { Fragment } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setSidePaneState } from "./features/chatbox";
import { setChatNew } from "./features/chatlist";

export default function ChatInfoComponent(props) {
  const dispatch = useDispatch();
  const sidePaneState = useSelector((state) => state.sidePaneState.value);
  const sidePaneEl = document.getElementById("sidepane");
  const chatBoxEl = document.getElementById("chatbox");

  function handleShowSideBar(e) {
    // dispatch(setChatNew(null));
    dispatch(setSidePaneState(true));
  }

  useEffect(function () {
    if (sidePaneState) {
      sidePaneEl.classList.add("shown");
      chatBoxEl.classList.add("minimized");
    }
    else {
      sidePaneEl.classList.remove("shown");
      chatBoxEl.classList.remove("minimized");
    }
  }, [sidePaneState]);

  return (
    <Fragment>
      <button onClick={handleShowSideBar}>&lt;-</button>
    </Fragment>
  );
}
