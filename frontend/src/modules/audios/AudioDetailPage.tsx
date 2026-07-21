import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Spinner } from "react-bootstrap";
import { MdArrowBack, MdAudiotrack, MdDownload } from "react-icons/md";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ProjectSelectorDropdown from "../../components/common/ProjectSelectorDropdown";
import { mediaService } from "../../services/media.service";
import type { Audio } from "../../types";

export default function AudioDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [audio, setAudio] = useState<Audio | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [updating, setUpdating] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await mediaService.listAudios(1, 100);
      const found = res.items.find((a) => a.id === id);
      if (!found) { toast.error("Audio not found"); navigate("/audios"); return; }
      setAudio(found);
      setSelectedProjects(found.project_ids ?? []);
    } catch {
      toast.error("Failed to load audio");
      navigate("/audios");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { load(); }, [load]);

  const handleUpdate = async () => {
    if (!id) return;
    setUpdating(true);
    try {
      const updated = await mediaService.updateAudio(id, { project_ids: selectedProjects });
      setAudio(updated);
      setSelectedProjects(updated.project_ids ?? []);
      toast.success("Projects updated");
    } catch {
      toast.error("Failed to update");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <Loader />;
  if (!audio) return null;

  const promptLines = audio.prompt?.split("\n").filter((l) => l.trim()) ?? [];
  const orig = (audio.project_ids ?? []).slice().sort().join(",");
  const curr = selectedProjects.slice().sort().join(",");
  const changed = orig !== curr;

  return (
    <div>
      <div className="page-header">
        <div className="d-flex align-items-center gap-2">
          <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate("/audios")}>
            <MdArrowBack size={22} />
          </Button>
          <h1 className="page-title" title={audio.title}>{audio.title}</h1>
        </div>
        <div className="d-flex align-items-center gap-2">
          <ProjectSelectorDropdown value={selectedProjects} onChange={setSelectedProjects} disabled={updating} />
          <Button className="btn-accent" size="sm" disabled={!changed || updating} onClick={handleUpdate}>
            {updating ? <Spinner size="sm" /> : "Update"}
          </Button>
        </div>
      </div>

      <div className="stat-card mb-4">
        {audio.file_url ? (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-3">
              <div className="d-flex align-items-center gap-2">
                <MdAudiotrack size={20} style={{ color: "var(--accent)" }} />
                <span className="fw-semibold">Audio Playback</span>
              </div>
              <a href={audio.file_url} download title="Download audio" className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1">
                <MdDownload size={16} /> Download
              </a>
            </div>
            <audio controls className="w-100" src={audio.file_url} style={{ borderRadius: 8 }}>
              Your browser does not support audio.
            </audio>
          </div>
        ) : (
          <div className="text-center py-3" style={{ color: "var(--muted)" }}>
            <MdAudiotrack size={32} className="mb-1" style={{ opacity: 0.4 }} />
            <p className="mb-0 small">No audio generated for this entry</p>
          </div>
        )}
      </div>

      {audio.prompt && (
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
