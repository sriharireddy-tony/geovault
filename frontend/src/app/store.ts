import { combineReducers, configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import prefsReducer from "./prefsSlice";

const rootReducer = combineReducers({
  auth: authReducer,
  prefs: prefsReducer,
});

export const store = configureStore({
  reducer: rootReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;
