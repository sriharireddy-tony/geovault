import { useState } from "react";
import { Form, Button, Alert, Spinner } from "react-bootstrap";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { login } from "../../app/authSlice";

export default function LoginPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { loading, error, token, user } = useAppSelector((s: any) => s.auth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (token && user) return <Navigate to="/" replace />;

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await dispatch(login({ email, password }));
    if (login.fulfilled.match(res)) navigate("/");
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-brand-icon" />
          <div>
            <h4 className="mb-0 fw-bold">AI Generator</h4>
            <small style={{ color: "var(--muted)" }}>Sign in to your account</small>
          </div>
        </div>

        {error && <Alert variant="danger" className="py-2 small">{error}</Alert>}

        <Form onSubmit={onSubmit}>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Email</Form.Label>
            <Form.Control type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="admin@example.com" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Password</Form.Label>
            <Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </Form.Group>
          <Button type="submit" className="btn-accent w-100" disabled={loading}>
            {loading ? <Spinner size="sm" /> : "Sign In"}
          </Button>
        </Form>

        <p className="text-center mt-3 mb-0 small" style={{ color: "var(--muted)" }}>
          Don't have an account? <Link to="/signup" className="text-accent">Create one</Link>
        </p>
      </div>
    </div>
  );
}
