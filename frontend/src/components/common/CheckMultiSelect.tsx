import { useEffect, useRef, useState } from "react";
import { MdCheck, MdExpandMore } from "react-icons/md";

export interface CheckOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

interface Props {
  options: CheckOption[];
  value: Set<string>;
  onChange: (ids: Set<string>) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function CheckMultiSelect({ options, value, onChange, placeholder = "Select...", disabled }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = (id: string) => {
    const next = new Set(value);
    if (next.has(id)) next.delete(id); else next.add(id);
    onChange(next);
  };

  const nameMap = new Map(options.map((o) => [o.value, o.label]));
  const selected = [...value];

  let displayText = placeholder;
  if (selected.length === 1) {
    displayText = nameMap.get(selected[0]) ?? "1 selected";
  } else if (selected.length > 1) {
    const first = nameMap.get(selected[0]) ?? "Item";
    displayText = `${first} +${selected.length - 1}`;
  }

  return (
    <div className="psd-wrapper" ref={ref} style={{ display: "block" }}>
      <button
        type="button"
        className="psd-trigger"
        style={{ width: "100%", maxWidth: "none" }}
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
      >
        <span className="psd-trigger-text">{displayText}</span>
        <MdExpandMore size={16} className={`psd-chevron${open ? " open" : ""}`} />
      </button>
      {open && (
        <div className="psd-menu" style={{ width: "100%" }}>
          {options.length === 0 ? (
            <div className="psd-empty">No items</div>
          ) : (
            options.map((o) => {
              const isSelected = value.has(o.value);
              return (
                <button
                  key={o.value}
                  type="button"
                  className={`psd-option${isSelected ? " selected" : ""}`}
                  onClick={() => toggle(o.value)}
                >
                  <span className="d-flex align-items-center gap-2 psd-option-text">
                    {o.icon}
                    {o.label}
                  </span>
                  {isSelected && <MdCheck size={15} className="psd-check" />}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
