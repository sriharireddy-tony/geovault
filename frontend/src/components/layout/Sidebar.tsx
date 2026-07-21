import { NavLink } from "react-router-dom";
import {
  MdDashboard,
  MdPeople,
  MdAudiotrack,
  MdImage,
  MdVideocam,
  MdFolder,
  MdEdit,
  MdMenuBook,
  MdChevronLeft,
  MdChevronRight,
} from "react-icons/md";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { toggleSidebar } from "../../app/prefsSlice";

const NAV = [
  { to: "/", icon: MdDashboard, label: "Dashboard" },
  { to: "/users", icon: MdPeople, label: "Users" },
  { to: "/projects", icon: MdFolder, label: "Projects" },
  { to: "/knowledge", icon: MdMenuBook, label: "Knowledge" },
  { to: "/audios", icon: MdAudiotrack, label: "Audios" },
  { to: "/images", icon: MdImage, label: "Images" },
  { to: "/videos", icon: MdVideocam, label: "Videos" },
  { to: "/editor", icon: MdEdit, label: "Editor" },
];

export default function Sidebar() {
  const collapsed = useAppSelector((s) => s.prefs.sidebarCollapsed);
  const dispatch = useAppDispatch();

  return (
    <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon" />
        <span className="sidebar-label fw-bold fs-6">GeoVault</span>
      </div>
      <nav className="sidebar-nav">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}>
            <Icon />
            <span className="sidebar-label">{label}</span>
          </NavLink>
        ))}
      </nav>
      <button
        className="sidebar-collapse-btn"
        onClick={() => dispatch(toggleSidebar())}
        title={collapsed ? "Expand" : "Collapse"}
      >
        {collapsed ? <MdChevronRight size={18} /> : <MdChevronLeft size={18} />}
      </button>
    </aside>
  );
}
