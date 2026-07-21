import { MdAudiotrack, MdImage, MdVideocam, MdFolder, MdPeople } from "react-icons/md";
import { useAppSelector } from "../app/hooks";

export default function Dashboard() {
  const user = useAppSelector((s) => s.auth.user);

  const cards = [
    { icon: MdPeople, label: "Users", color: "#6366f1" },
    { icon: MdAudiotrack, label: "Audios", color: "#f59e0b" },
    { icon: MdImage, label: "Images", color: "#10b981" },
    { icon: MdVideocam, label: "Videos", color: "#f43f5e" },
    { icon: MdFolder, label: "Projects", color: "#0ea5e9" },
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Welcome back, {user?.first_name}</h1>
      </div>
      <div className="row g-3">
        {cards.map((c) => (
          <div key={c.label} className="col-6 col-md-4 col-xl">
            <div className="stat-card d-flex align-items-center gap-3">
              <div
                className="d-flex align-items-center justify-content-center rounded-3"
                style={{ width: 48, height: 48, background: `${c.color}22`, color: c.color }}
              >
                <c.icon size={24} />
              </div>
              <div>
                <div className="small" style={{ color: "var(--muted)" }}>{c.label}</div>
                <div className="fw-bold fs-5">—</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 p-4 stat-card text-center" style={{ color: "var(--muted)" }}>
        <p className="mb-0">Dashboard analytics coming soon.</p>
      </div>
    </div>
  );
}
