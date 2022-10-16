import { useSelector } from "react-redux";
import { useVerifyUserQuery } from "./api/auth";

export default function UserComponent(props) {
  useVerifyUserQuery();

  const currentUser = useSelector((state) => state.currentUser.value);

  return (
    <div>{currentUser} <button>Logout</button></div>
  );
}
