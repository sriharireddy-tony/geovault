import { useCallback, useEffect, useState } from "react";
import { MdFolder, MdInbox, MdApps } from "react-icons/md";
import { projectService } from "../../services/project.service";
import type { Project } from "../../types";

interface Props {
  selected: string;
  onSelect: (projectId: string, projectName?: string) => void;
}

export default function ProjectFilterSidebar({ selected, onSelect }: Props) {
  const [projects, setProjects] = useState<Project[]>([]);

  const load = useCallback(async () => {
    try {
      const res = await projectService.list(1, 200);
      setProjects(res.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="project-filter">
      <div className="project-filter-header">Projects</div>
      <button
        className={`project-filter-item${selected === "" ? " active" : ""}`}
        onClick={() => onSelect("", "All Projects")}
      >
        <MdApps size={16} />
        <span>All</span>
      </button>
      <button
        className={`project-filter-item${selected === "others" ? " active" : ""}`}
        onClick={() => onSelect("others", "Others (no project)")}
      >
        <MdInbox size={16} />
        <span>Others</span>
      </button>
      {projects.map((p) => (
        <button
          key={p.id}
          className={`project-filter-item${selected === p.id ? " active" : ""}`}
          onClick={() => onSelect(p.id, p.title)}
          title={p.title}
        >
          <MdFolder size={16} />
          <span>{p.title}</span>
        </button>
      ))}
    </div>
  );
}
