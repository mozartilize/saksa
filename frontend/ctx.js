import Cookies from "js-cookie";
import React from "react";

export const UsernameCtx = React.createContext(Cookies.get("username"));

export const SelectedChatIdCtx = React.createContext("f8680106-a790-4b6e-912f-7adb93f2a69a");
