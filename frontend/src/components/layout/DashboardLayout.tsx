import { useState } from "react";
import { Outlet } from "react-router-dom";
import { useAppSelector } from "../../app/hooks";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import EditProfileModal from "../../modules/auth/EditProfileModal";
import PreferencesModal from "../../modules/auth/PreferencesModal";

export default function DashboardLayout() {
  const collapsed = useAppSelector((s) => s.prefs.sidebarCollapsed);
  const [showProfile, setShowProfile] = useState(false);
  const [showPrefs, setShowPrefs] = useState(false);

  return (
    <>
      <Sidebar />
      <Topbar onEditProfile={() => setShowProfile(true)} onPreferences={() => setShowPrefs(true)} />
      <div className={`main-content${collapsed ? " sidebar-collapsed" : ""}`}>
        <Outlet />
      </div>
      <EditProfileModal show={showProfile} onHide={() => setShowProfile(false)} />
      <PreferencesModal show={showPrefs} onHide={() => setShowPrefs(false)} />
    </>
  );
}
