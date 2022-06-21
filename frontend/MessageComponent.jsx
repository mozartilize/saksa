import { useSelector } from "react-redux";

export default function MessageComponent(props) {
    const currentUser = useSelector(state => state.currentUser.value);
    const classNames = [
        "message",
        props.message.sender === currentUser ? "isOut" : "isIn",
    ];
    return (
        <div className={classNames.join(" ")}>
            <div>
                {props.message.message}
            </div>
        </div>
    )
}