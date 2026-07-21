import { useCallback, useEffect, useRef, useState } from "react";
import { MdCheck, MdExpandMore } from "react-icons/md";
import { projectService } from "../../services/project.service";
import type { Project } from "../../types";

interface Props {
  value: string[];
  onChange: (projectIds: string[]) => void;
  disabled?: boolean;
}

export default function ProjectSelectorDropdown({ value, onChange, disabled }: Props) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    try {
      const res = await projectService.list(1, 500);
      setProjects(res.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  const nameMap = new Map(projects.map((p) => [p.id, p.title]));

  let displayText = "Select projects...";
  if (value.length === 1) {
    displayText = nameMap.get(value[0]) ?? "1 selected";
  } else if (value.length > 1) {
    const firstName = nameMap.get(value[0]) ?? "Item";
    displayText = `${firstName} +${value.length - 1}`;
  }

  return (
    <div className="psd-wrapper" ref={ref}>
      <button
        type="button"
        className="psd-trigger"
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
      >
        <span className="psd-trigger-text">{displayText}</span>
        <MdExpandMore size={16} className={`psd-chevron${open ? " open" : ""}`} />
      </button>
      {open && (
        <div className="psd-menu">
          {projects.length === 0 ? (
            <div className="psd-empty">No projects</div>
          ) : (
            projects.map((p) => {
              const selected = value.includes(p.id);
              return (
                <button
                  key={p.id}
                  type="button"
                  className={`psd-option${selected ? " selected" : ""}`}
                  onClick={() => toggle(p.id)}
                  title={p.title}
                >
                  <span className="psd-option-text">{p.title}</span>
                  {selected && <MdCheck size={15} className="psd-check" />}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
