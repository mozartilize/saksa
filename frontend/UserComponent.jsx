import { useSelector } from "react-redux";
import { useVerifyUserQuery } from "./api/auth";

export default function UserComponent(props) {
  useVerifyUserQuery();

  const currentUser = useSelector((state) => state.currentUser.value);

  function logout() {
    document.cookie = "username" +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    location.reload();
  }

  return (
    <div>{currentUser} <button onClick={logout}>Logout</button></div>
  );
}
