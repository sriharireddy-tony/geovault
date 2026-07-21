import { Modal, Form, Button } from "react-bootstrap";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { setThemeMode, setThemeColor, savePreferences, type ThemeMode } from "../../app/prefsSlice";
import { toast } from "react-toastify";

const PRESETS = [
  { label: "Indigo", value: "#6366f1" },
  { label: "Rose", value: "#f43f5e" },
  { label: "Emerald", value: "#10b981" },
  { label: "Amber", value: "#f59e0b" },
  { label: "Sky", value: "#0ea5e9" },
  { label: "Violet", value: "#8b5cf6" },
];

interface Props {
  show: boolean;
  onHide: () => void;
}

export default function PreferencesModal({ show, onHide }: Props) {
  const dispatch = useAppDispatch();
  const { themeMode, themeColor } = useAppSelector((s) => s.prefs);

  const save = async () => {
    try {
      await dispatch(savePreferences({ theme_mode: themeMode, theme_color: themeColor })).unwrap();
      toast.success("Preferences saved");
      onHide();
    } catch {
      toast.error("Failed to save preferences");
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Preferences</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group className="mb-3">
          <Form.Label className="small fw-medium">Theme Mode</Form.Label>
          <Form.Select
            value={themeMode}
            onChange={(e) => dispatch(setThemeMode(e.target.value as ThemeMode))}
          >
            <option value="system">System</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </Form.Select>
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label className="small fw-medium">Accent Color</Form.Label>
          <div className="d-flex align-items-center gap-2 flex-wrap">
            <Form.Control
              type="color"
              value={themeColor}
              onChange={(e) => dispatch(setThemeColor(e.target.value))}
              style={{ width: 48, height: 38, padding: 2, border: "1px solid var(--border)" }}
            />
            {PRESETS.map((p) => (
              <button
                key={p.value}
                type="button"
                title={p.label}
                onClick={() => dispatch(setThemeColor(p.value))}
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: p.value,
                  border: themeColor === p.value ? "2px solid var(--text)" : "2px solid transparent",
                  cursor: "pointer",
                  padding: 0,
                }}
              />
            ))}
          </div>
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Close</Button>
        <Button className="btn-accent" onClick={save}>Save</Button>
      </Modal.Footer>
    </Modal>
  );
}
