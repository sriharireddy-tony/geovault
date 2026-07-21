import { useCallback, useEffect, useState } from "react";
import { Button, Modal, Form, Spinner, Pagination } from "react-bootstrap";
import { MdPerson } from "react-icons/md";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ConfirmModal from "../../components/common/ConfirmModal";
import { userService } from "../../services/user.service";
import { useAppSelector } from "../../app/hooks";
import type { User } from "../../types";
import { formatDate } from "../../utils";

const ROLE_COLORS: Record<string, string> = {
  SUPER_ADMIN: "#8b5cf6",
  ADMIN: "#3b82f6",
  USER: "#10b981",
};

export default function UsersPage() {
  const role = useAppSelector((s) => s.auth.user?.role);
  const isAdmin = role === "ADMIN" || role === "SUPER_ADMIN";
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);

  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "", role: "USER" });
  const set = (key: string, val: string) => setForm((p) => ({ ...p, [key]: val }));

  const load = useCallback(async (p: number) => {
    setLoading(true);
    try {
      const res = await userService.list(p);
      setUsers(res.items);
      setPages(res.pages);
      setPage(res.page);
    } catch {
      toast.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(1); }, [load]);

  const handleDeactivate = async () => {
    if (!deactivateId) return;
    try {
      await userService.deactivate(deactivateId);
      toast.success("User deactivated");
      setDeactivateId(null);
      load(page);
    } catch {
      toast.error("Failed to deactivate user");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await userService.create(form);
      toast.success("User created");
      setShowCreate(false);
      setForm({ email: "", password: "", first_name: "", last_name: "", role: "USER" });
      load(page);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to create user");
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Users</h1>
        {isAdmin && <Button className="btn-accent" onClick={() => setShowCreate(true)}>+ Create User</Button>}
      </div>

      {users.length === 0 ? (
        <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
          <MdPerson size={48} className="mb-2" style={{ opacity: 0.3 }} />
          <p className="mb-0">No users found.</p>
        </div>
      ) : (
        <>
          <div className="row g-3">
            {users.map((u) => (
              <div key={u.id} className="col-lg-3 col-md-4 col-sm-6">
                <div className="user-card">
                  <div className="user-card-body">
                    <div className="user-card-avatar" style={{ background: `${ROLE_COLORS[u.role] ?? "#6b7280"}20`, color: ROLE_COLORS[u.role] ?? "#6b7280" }}>
                      <MdPerson size={22} />
                    </div>
                    <h6 className="user-card-name" title={`${u.first_name} ${u.last_name}`}>{u.first_name} {u.last_name}</h6>
                    <p className="user-card-email" title={u.email}>{u.email}</p>
                    <span className="user-card-role" style={{ background: `${ROLE_COLORS[u.role] ?? "#6b7280"}18`, color: ROLE_COLORS[u.role] ?? "#6b7280" }}>
                      {u.role}
                    </span>
                    {!u.is_active && <span className="user-card-role" style={{ background: "#ef444418", color: "#ef4444", marginLeft: 4 }}>Inactive</span>}
                  </div>
                  <div className="user-card-footer">
                    <span>{formatDate(u.created_at)}</span>
                    {isAdmin && u.is_active && (
                      <Button size="sm" variant="outline-danger" style={{ fontSize: "0.7rem", padding: "2px 8px" }} onClick={() => setDeactivateId(u.id)}>
                        Deactivate
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {pages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Pagination size="sm" className="mb-0">
                <Pagination.Prev disabled={page <= 1} onClick={() => load(page - 1)} />
                {Array.from({ length: Math.min(pages, 7) }, (_, i) => i + 1).map((p) => (
                  <Pagination.Item key={p} active={p === page} onClick={() => load(p)}>{p}</Pagination.Item>
                ))}
                {pages > 7 && <Pagination.Ellipsis disabled />}
                <Pagination.Next disabled={page >= pages} onClick={() => load(page + 1)} />
              </Pagination>
            </div>
          )}
        </>
      )}

      <ConfirmModal
        show={!!deactivateId}
        message="Are you sure you want to deactivate this user?"
        confirmLabel="Deactivate"
        onConfirm={handleDeactivate}
        onCancel={() => setDeactivateId(null)}
      />

      <Modal show={showCreate} onHide={() => setShowCreate(false)} centered>
        <Modal.Header closeButton><Modal.Title>Create User</Modal.Title></Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
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
              <Form.Control type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Password</Form.Label>
              <Form.Control type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required minLength={8} />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Role</Form.Label>
              <Form.Select value={form.role} onChange={(e) => set("role", e.target.value)}>
                <option value="USER">User</option>
                <option value="ADMIN">Admin</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={creating}>{creating ? <Spinner size="sm" /> : "Create"}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
}
