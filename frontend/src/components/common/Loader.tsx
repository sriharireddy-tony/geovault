import { Spinner } from "react-bootstrap";

export default function Loader({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="d-flex align-items-center justify-content-center py-5 gap-2" style={{ color: "var(--muted)" }}>
      <Spinner animation="border" size="sm" />
      <span>{text}</span>
    </div>
  );
}
