import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page" style={{ display: "flex", justifyContent: "center", paddingTop: 80 }}><div className="spinner" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export function PublicOnlyRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page" style={{ display: "flex", justifyContent: "center", paddingTop: 80 }}><div className="spinner" /></div>;
  if (user) return <Navigate to="/feed" replace />;
  return children;
}
