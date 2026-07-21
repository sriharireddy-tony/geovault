import { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useAppDispatch, useAppSelector } from "./app/hooks";
import { fetchMe } from "./app/authSlice";
import { loadPreferences } from "./app/prefsSlice";
import AppRoutes from "./routes/AppRoutes";
import Loader from "./components/common/Loader";

export default function App() {
  const dispatch = useAppDispatch();
  const { token, loading, user } = useAppSelector((s) => s.auth);

  useEffect(() => {
    if (token && !user) {
      dispatch(fetchMe());
      dispatch(loadPreferences());
    }
  }, [dispatch, token, user]);

  if (token && loading && !user) return <Loader text="Loading..." />;

  return (
    <BrowserRouter>
      <AppRoutes />
      <ToastContainer position="top-right" autoClose={3000} theme="colored" />
    </BrowserRouter>
  );
}
