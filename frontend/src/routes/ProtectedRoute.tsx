import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAppSelector } from "../app/hooks";
import Loader from "../components/common/Loader";

export default function ProtectedRoute() {
  const { token, user, loading } = useAppSelector((s) => s.auth);
  const location = useLocation();

  // Token exists but user not yet fetched — wait for fetchMe() to complete
  if (token && !user) return <Loader text="Authenticating..." />;
  if (loading) return <Loader text="Authenticating..." />;
  if (!token) return <Navigate to="/login" state={{ from: location }} replace />;

  return <Outlet />;
}
