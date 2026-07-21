import { Form } from "react-bootstrap";

interface Props {
  label: string;
  type?: string;
  value: string;
  onChange: (val: string) => void;
  required?: boolean;
  placeholder?: string;
  as?: "input" | "textarea" | "select";
  rows?: number;
  children?: React.ReactNode;
}

export default function FormInput({
  label,
  type = "text",
  value,
  onChange,
  required = false,
  placeholder,
  as = "input",
  rows,
  children,
}: Props) {
  return (
    <Form.Group className="mb-3">
      <Form.Label className="small fw-medium">{label}</Form.Label>
      {as === "select" ? (
        <Form.Select value={value} onChange={(e) => onChange(e.target.value)} required={required}>
          {children}
        </Form.Select>
      ) : (
        <Form.Control
          type={type}
          as={as === "textarea" ? "textarea" : undefined}
          rows={rows}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          placeholder={placeholder}
        />
      )}
    </Form.Group>
  );
}
