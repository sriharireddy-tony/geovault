import { Dropdown } from "react-bootstrap";
import { MdPerson, MdSettings, MdLogout } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { logout } from "../../app/authSlice";

interface Props {
  onEditProfile: () => void;
  onPreferences: () => void;
}

export default function Topbar({ onEditProfile, onPreferences }: Props) {
  const collapsed = useAppSelector((s: any) => s.prefs.sidebarCollapsed);
  const user = useAppSelector((s: any) => s.auth.user);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  const initials = user
    ? `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase()
    : "?";

  const roleLabel = user?.role === "SUPER_ADMIN" ? "Super Admin" : user?.role === "ADMIN" ? "Admin" : "User";

  return (
    <div className={`topbar${collapsed ? " sidebar-collapsed" : ""}`}>
      <div />
      <Dropdown align="end">
        <Dropdown.Toggle variant="link" className="profile-toggle text-decoration-none p-0" style={{ color: "var(--text)" }}>
          <div className="profile-avatar">{initials}</div>
        </Dropdown.Toggle>
        <Dropdown.Menu className="profile-dropdown">
          <div className="profile-dropdown-header">
            <div className="fw-semibold">{user?.first_name} {user?.last_name}</div>
            <small style={{ color: "var(--muted)" }}>{roleLabel}</small>
          </div>
          <Dropdown.Divider />
          <Dropdown.Item onClick={onEditProfile}>
            <MdPerson className="me-2" size={16} /> Edit Profile
          </Dropdown.Item>
          <Dropdown.Item onClick={onPreferences}>
            <MdSettings className="me-2" size={16} /> Preferences
          </Dropdown.Item>
          <Dropdown.Divider />
          <Dropdown.Item onClick={handleLogout} className="text-danger">
            <MdLogout className="me-2" size={16} /> Logout
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    </div>
  );
}
