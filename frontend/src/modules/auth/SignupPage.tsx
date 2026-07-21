import { useState } from "react";
import { Form, Button, Alert, Spinner } from "react-bootstrap";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { signup } from "../../app/authSlice";

export default function SignupPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { loading, error, token, user } = useAppSelector((s: any) => s.auth);
  const [form, setForm] = useState({
    tenant_name: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  });

  const set = (key: string, val: string) => setForm((p) => ({ ...p, [key]: val }));

  if (token && user) return <Navigate to="/" replace />;

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await dispatch(signup(form));
    if (signup.fulfilled.match(res)) navigate("/");
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-brand-icon" />
          <div>
            <h4 className="mb-0 fw-bold">AI Generator</h4>
            <small style={{ color: "var(--muted)" }}>Create your account</small>
          </div>
        </div>

        {error && <Alert variant="danger" className="py-2 small">{error}</Alert>}

        <Form onSubmit={onSubmit}>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Organization Name</Form.Label>
            <Form.Control value={form.tenant_name} onChange={(e) => set("tenant_name", e.target.value)} required placeholder="My Company" />
          </Form.Group>
          <div className="row">
            <div className="col-6">
              <Form.Group className="mb-3">
                <Form.Label className="small fw-medium">First Name</Form.Label>
                <Form.Control value={form.first_name} onChange={(e) => set("first_name", e.target.value)} required />
              </Form.Group>
            </div>
            <div className="col-6">
              <Form.Group className="mb-3">
                <Form.Label className="small fw-medium">Last Name</Form.Label>
                <Form.Control value={form.last_name} onChange={(e) => set("last_name", e.target.value)} required />
              </Form.Group>
            </div>
          </div>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Email</Form.Label>
            <Form.Control type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required placeholder="admin@example.com" />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Password</Form.Label>
            <Form.Control type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required minLength={8} placeholder="Min 8 characters" />
          </Form.Group>
          <Button type="submit" className="btn-accent w-100" disabled={loading}>
            {loading ? <Spinner size="sm" /> : "Create Account"}
          </Button>
        </Form>

        <p className="text-center mt-3 mb-0 small" style={{ color: "var(--muted)" }}>
          Already have an account? <Link to="/login" className="text-accent">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
