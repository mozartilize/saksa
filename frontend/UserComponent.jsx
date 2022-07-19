import { Fragment } from "react";
import { useVerifyUserQuery } from "./api/auth";

export default function UserComponent(props) {
  useVerifyUserQuery();
  return <Fragment></Fragment>;
}
