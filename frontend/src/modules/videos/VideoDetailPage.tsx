import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Spinner } from "react-bootstrap";
import { MdArrowBack, MdVideocam, MdDownload } from "react-icons/md";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ProjectSelectorDropdown from "../../components/common/ProjectSelectorDropdown";
import { mediaService } from "../../services/media.service";
import type { Video } from "../../types";

export default function VideoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [video, setVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [updating, setUpdating] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await mediaService.listVideos(1, 100);
      const found = res.items.find((v) => v.id === id);
      if (!found) { toast.error("Video not found"); navigate("/videos"); return; }
      setVideo(found);
      setSelectedProjects(found.project_ids ?? []);
    } catch {
      toast.error("Failed to load video");
      navigate("/videos");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { load(); }, [load]);

  const handleUpdate = async () => {
    if (!id) return;
    setUpdating(true);
    try {
      const updated = await mediaService.updateVideo(id, { project_ids: selectedProjects });
      setVideo(updated);
      setSelectedProjects(updated.project_ids ?? []);
      toast.success("Projects updated");
    } catch {
      toast.error("Failed to update");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <Loader />;
  if (!video) return null;

  const promptLines = video.prompt?.split("\n").filter((l) => l.trim()) ?? [];
  const orig = (video.project_ids ?? []).slice().sort().join(",");
  const curr = selectedProjects.slice().sort().join(",");
  const changed = orig !== curr;

  return (
    <div>
      <div className="page-header">
        <div className="d-flex align-items-center gap-2">
          <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate("/videos")}>
            <MdArrowBack size={22} />
          </Button>
          <h1 className="page-title" title={video.title}>{video.title}</h1>
        </div>
        <div className="d-flex align-items-center gap-2">
          <ProjectSelectorDropdown value={selectedProjects} onChange={setSelectedProjects} disabled={updating} />
          <Button className="btn-accent" size="sm" disabled={!changed || updating} onClick={handleUpdate}>
            {updating ? <Spinner size="sm" /> : "Update"}
          </Button>
        </div>
      </div>

      <div className="stat-card mb-4">
        {video.file_url ? (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-3">
              <div className="d-flex align-items-center gap-2">
                <MdVideocam size={20} style={{ color: "var(--accent)" }} />
                <span className="fw-semibold">Video Playback</span>
              </div>
              <a href={video.file_url} download title="Download video" className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1">
                <MdDownload size={16} /> Download
              </a>
            </div>
            <video controls className="w-100 rounded" src={video.file_url} style={{ maxHeight: 400 }}>
              Your browser does not support video.
            </video>
          </div>
        ) : (
          <div className="text-center py-3" style={{ color: "var(--muted)" }}>
            <MdVideocam size={32} className="mb-1" style={{ opacity: 0.4 }} />
            <p className="mb-0 small">No video file generated yet</p>
          </div>
        )}
      </div>

      {video.prompt && (
        <div className="mb-4">
          <h6 className="fw-semibold mb-3">Prompt Text</h6>
          <div className="detail-prompt">
            {promptLines.map((line, i) => (
              <div key={i} className="mb-1">{line}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
