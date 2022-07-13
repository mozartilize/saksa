import { Fragment } from 'react';
import { useSelector } from "react-redux";
import { useVerifyUserQuery } from "./api/auth";

export default function UserComponent(props) {
  const currentUser = useSelector(state => state.currentUser.value);

  useVerifyUserQuery(currentUser);
  return (
    <Fragment></Fragment>
  )
}
