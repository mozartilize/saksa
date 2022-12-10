import {
  Fragment,
  useEffect,
  useState,
  useCallback,
  useRef,
} from "react";
import { useDispatch, useSelector } from "react-redux";

import MessageComponent from "./MessageComponent";
import { messagesApi } from "./api/messages";
import { prependMessages } from "./features/chatbox";

function getInitialCursor() {
  return new Date().getTime() / 1000 + new Date().getTimezoneOffset() * 60;
}

export default function MessagesComponent(props) {
  const dispatch = useDispatch();
  const wrapperEl = useRef(null);
  const selectingChat = useSelector((state) => state.selectingChat.value);
  const [cursor, setCursor] = useState(getInitialCursor());
  const [clientHeight, setClientHeight] = useState(0);
  const [scrollHeight, setScrollHeight] = useState(0);
  // unless we on the bottom, there is no need to auto scroll to bottom
  const [needScrollBottom, setNeedScrollBottom] = useState(true);

  const items = useSelector((state) => state.chatMessages.value);

  const { data, status, error } = useSelector((state) =>
    messagesApi.endpoints.fetchMessages.select({
      selectingChatId: selectingChat ? selectingChat.chat_id : null,
      cursor,
    })(state)
  );

  useEffect(() => {
    if (selectingChat && selectingChat.chat_id) {
      dispatch(
        messagesApi.endpoints.fetchMessages.initiate({
          selectingChatId: selectingChat.chat_id,
          cursor,
        })
      );
    }
    if (data) {
      dispatch(prependMessages(data));
    }
  }, [selectingChat, cursor, data, status, error]);

  useEffect(() => {
    if (
      data &&
      data.length > 0 &&
      clientHeight !== 0 &&
      scrollHeight <= clientHeight
    ) {
      setCursor(data[0].created_at);
    }
  }, [clientHeight, scrollHeight, data, status, error]);

  const measuredRef = useCallback(
    (node) => {
      if (node !== null) {
        setClientHeight(node.clientHeight);
        setScrollHeight(node.scrollHeight);
        if (!wrapperEl.current) {
          wrapperEl.current = node;
        }
      }
    },
    [clientHeight, scrollHeight, data, status, error]
  );

  const handleScrollEvent = (e) => {
    const el = wrapperEl.current;
    if (data && data.length > 0 && wrapperEl.current.scrollTop === 0) {
      setCursor(data[0].created_at);
    }
    if (el.clientHeight + el.scrollTop >= el.scrollHeight) {
      setNeedScrollBottom(true);
    } else {
      setNeedScrollBottom(false);
    }
  };

  useEffect(() => {
    if (wrapperEl.current && needScrollBottom) {
      wrapperEl.current.scrollTop = wrapperEl.current.scrollHeight;
    } else if (wrapperEl.current && !needScrollBottom) {
      // keep scroll bar at current position,
      // if not, the view will be on top after history load
      wrapperEl.current.scrollTop =
        wrapperEl.current.scrollHeight - scrollHeight;
    }
  }, [items]);

  return items.length === 0 ? (
    <Fragment></Fragment>
  ) : (
    <div
      onScroll={handleScrollEvent}
      style={{ height: "100%", overflowY: "scroll" }}
      ref={measuredRef}
    >
      {items.map((message) => (
        <MessageComponent key={message.created_at} message={message} />
      ))}
    </div>
  );
}
