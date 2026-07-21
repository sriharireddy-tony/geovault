import { useState, useEffect } from "react";
import { Modal, Form, Button, Spinner } from "react-bootstrap";
import { toast } from "react-toastify";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { setUser } from "../../app/authSlice";
import { authService } from "../../services/auth.service";

interface Props {
  show: boolean;
  onHide: () => void;
}

export default function EditProfileModal({ show, onHide }: Props) {
  const user = useAppSelector((s) => s.auth.user);
  const dispatch = useAppDispatch();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (user && show) {
      setFirstName(user.first_name);
      setLastName(user.last_name);
      setPassword("");
    }
  }, [user, show]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const payload: Record<string, string> = {};
      if (firstName !== user?.first_name) payload.first_name = firstName;
      if (lastName !== user?.last_name) payload.last_name = lastName;
      if (password) payload.password = password;
      const updated = await authService.updateProfile(payload);
      dispatch(setUser(updated));
      toast.success("Profile updated");
      onHide();
    } catch {
      toast.error("Failed to update profile");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Edit Profile</Modal.Title>
      </Modal.Header>
      <Form onSubmit={onSubmit}>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">First Name</Form.Label>
            <Form.Control value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">Last Name</Form.Label>
            <Form.Control value={lastName} onChange={(e) => setLastName(e.target.value)} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label className="small fw-medium">New Password (optional)</Form.Label>
            <Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} placeholder="Leave blank to keep current" />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>Cancel</Button>
          <Button type="submit" className="btn-accent" disabled={busy}>
            {busy ? <Spinner size="sm" /> : "Save"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
