import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import DashboardLayout from "../components/layout/DashboardLayout";
import SignupPage from "../modules/auth/SignupPage";
import LoginPage from "../modules/auth/LoginPage";
import Dashboard from "../pages/Dashboard";
import UsersPage from "../modules/users/UsersPage";
import AudiosPage from "../modules/audios/AudiosPage";
import AudioDetailPage from "../modules/audios/AudioDetailPage";
import ImagesPage from "../modules/images/ImagesPage";
import ImageDetailPage from "../modules/images/ImageDetailPage";
import VideosPage from "../modules/videos/VideosPage";
import VideoDetailPage from "../modules/videos/VideoDetailPage";
import ProjectsPage from "../modules/projects/ProjectsPage";
import ProjectDetailPage from "../modules/projects/ProjectDetailPage";
import EditorPage from "../modules/editor/EditorPage";
import KnowledgeSpacesPage from "../modules/knowledge/KnowledgeSpacesPage";
import SpaceDetailPage from "../modules/knowledge/SpaceDetailPage";
import KnowledgeChatPage from "../modules/knowledge/KnowledgeChatPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="audios" element={<AudiosPage />} />
          <Route path="audios/:id" element={<AudioDetailPage />} />
          <Route path="images" element={<ImagesPage />} />
          <Route path="images/:id" element={<ImageDetailPage />} />
          <Route path="videos" element={<VideosPage />} />
          <Route path="videos/:id" element={<VideoDetailPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="projects/:id" element={<ProjectDetailPage />} />
          <Route path="knowledge" element={<KnowledgeSpacesPage />} />
          <Route path="knowledge/:spaceId" element={<SpaceDetailPage />} />
          <Route path="knowledge/:spaceId/chat" element={<KnowledgeChatPage />} />
          <Route path="editor" element={<EditorPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
