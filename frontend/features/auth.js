import Cookies from "js-cookie";
import { createSlice } from "@reduxjs/toolkit";

export const currentUser = createSlice({
  name: 'currentUser',
  initialState: {
    value: Cookies.get("username"),
  },
});
