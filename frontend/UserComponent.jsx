import { useSelector } from "react-redux";
import { useVerifyUserQuery } from "./api/auth";

export default function UserComponent(props) {
  useVerifyUserQuery();

  const currentUser = useSelector((state) => state.currentUser.value);

  function handleLogout() {
    document.cookie = 'username' +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    location.href = "/";
  }

  return (
    <div>{currentUser} <button onClick={handleLogout}>Logout</button></div>
  );
}
