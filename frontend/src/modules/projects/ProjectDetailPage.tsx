import { useCallback, useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Spinner } from "react-bootstrap";
import { MdArrowBack, MdAudiotrack, MdImage, MdVideocam } from "react-icons/md";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import CheckMultiSelect, { type CheckOption } from "../../components/common/CheckMultiSelect";
import MediaPreviewCard from "../../components/common/MediaPreviewCard";
import { projectService } from "../../services/project.service";
import type { ProjectDetail } from "../../types";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [selectedAudioIds, setSelectedAudioIds] = useState<Set<string>>(new Set());
  const [selectedImageIds, setSelectedImageIds] = useState<Set<string>>(new Set());
  const [selectedVideoIds, setSelectedVideoIds] = useState<Set<string>>(new Set());

  const applySelection = (proj: ProjectDetail) => {
    setSelectedAudioIds(new Set(proj.selected_media.audios.map((a) => a.id)));
    setSelectedImageIds(new Set(proj.selected_media.images.map((i) => i.id)));
    setSelectedVideoIds(new Set(proj.selected_media.videos.map((v) => v.id)));
  };

  const loadProject = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const proj = await projectService.get(id);
      setProject(proj);
      applySelection(proj);
    } catch {
      toast.error("Failed to load project");
      navigate("/projects");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { loadProject(); }, [loadProject]);

  const availAudios = project?.available_media.audios ?? [];
  const availImages = project?.available_media.images ?? [];
  const availVideos = project?.available_media.videos ?? [];

  const audioOptions: CheckOption[] = useMemo(() =>
    availAudios.map((a) => ({ value: a.id, label: a.title, icon: <MdAudiotrack size={14} style={{ color: "var(--accent)" }} /> })),
    [availAudios]);
  const imageOptions: CheckOption[] = useMemo(() =>
    availImages.map((i) => ({ value: i.id, label: i.title, icon: <MdImage size={14} style={{ color: "var(--accent)" }} /> })),
    [availImages]);
  const videoOptions: CheckOption[] = useMemo(() =>
    availVideos.map((v) => ({ value: v.id, label: v.title, icon: <MdVideocam size={14} style={{ color: "var(--accent)" }} /> })),
    [availVideos]);

  const audioMap = useMemo(() => new Map(availAudios.map((a) => [a.id, a])), [availAudios]);
  const imageMap = useMemo(() => new Map(availImages.map((i) => [i.id, i])), [availImages]);
  const videoMap = useMemo(() => new Map(availVideos.map((v) => [v.id, v])), [availVideos]);

  const handleSave = async () => {
    if (!id) return;
    setSaving(true);
    try {
      const updated = await projectService.updateSelection(id, {
        audio_ids: [...selectedAudioIds],
        image_ids: [...selectedImageIds],
        video_ids: [...selectedVideoIds],
      });
      setProject(updated);
      applySelection(updated);
      toast.success("Project updated");
    } catch {
      toast.error("Failed to update project");
    } finally {
      setSaving(false);
    }
  };

  const removeItem = (type: "audio" | "image" | "video", itemId: string) => {
    if (type === "audio") setSelectedAudioIds((prev) => { const n = new Set(prev); n.delete(itemId); return n; });
    if (type === "image") setSelectedImageIds((prev) => { const n = new Set(prev); n.delete(itemId); return n; });
    if (type === "video") setSelectedVideoIds((prev) => { const n = new Set(prev); n.delete(itemId); return n; });
  };

  if (loading) return <Loader />;
  if (!project) return null;

  const noMedia = availAudios.length === 0 && availImages.length === 0 && availVideos.length === 0;

  return (
    <div>
      <div className="page-header">
        <div className="d-flex align-items-center gap-2">
          <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate("/projects")}>
            <MdArrowBack size={22} />
          </Button>
          <h1 className="page-title">{project.title}</h1>
        </div>
        <Button className="btn-accent" onClick={handleSave} disabled={saving}>
          {saving ? <Spinner size="sm" /> : "Update Project"}
        </Button>
      </div>

      {noMedia ? (
        <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
          <MdAudiotrack size={40} className="mb-2" style={{ opacity: 0.3 }} />
          <p className="mb-1 fw-semibold">No media available in this project</p>
          <p className="mb-0 small">Create media first and assign it to this project.</p>
        </div>
      ) : (
        <>
          {/* Select for editing */}
          <div className="mb-2">
            <h6 className="fw-semibold" style={{ fontSize: "0.9rem", color: "var(--muted)" }}>Select for Editing</h6>
          </div>
          <div className="row g-3 mb-4">
            {availAudios.length > 0 && (
              <div className="col-lg-4 col-md-6">
                <div className="stat-card">
                  <div className="d-flex align-items-center gap-2 mb-2">
                    <MdAudiotrack size={18} style={{ color: "var(--accent)" }} />
                    <h6 className="fw-semibold mb-0" style={{ fontSize: "0.85rem" }}>Audios</h6>
                    <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)", fontSize: "0.65rem" }}>{availAudios.length} available</span>
                  </div>
                  <CheckMultiSelect options={audioOptions} value={selectedAudioIds} onChange={setSelectedAudioIds} placeholder="Select audios..." />
                </div>
              </div>
            )}
            {availImages.length > 0 && (
              <div className="col-lg-4 col-md-6">
                <div className="stat-card">
                  <div className="d-flex align-items-center gap-2 mb-2">
                    <MdImage size={18} style={{ color: "var(--accent)" }} />
                    <h6 className="fw-semibold mb-0" style={{ fontSize: "0.85rem" }}>Images</h6>
                    <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)", fontSize: "0.65rem" }}>{availImages.length} available</span>
                  </div>
                  <CheckMultiSelect options={imageOptions} value={selectedImageIds} onChange={setSelectedImageIds} placeholder="Select images..." />
                </div>
              </div>
            )}
            {availVideos.length > 0 && (
              <div className="col-lg-4 col-md-6">
                <div className="stat-card">
                  <div className="d-flex align-items-center gap-2 mb-2">
                    <MdVideocam size={18} style={{ color: "var(--accent)" }} />
                    <h6 className="fw-semibold mb-0" style={{ fontSize: "0.85rem" }}>Videos</h6>
                    <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)", fontSize: "0.65rem" }}>{availVideos.length} available</span>
                  </div>
                  <CheckMultiSelect options={videoOptions} value={selectedVideoIds} onChange={setSelectedVideoIds} placeholder="Select videos..." />
                </div>
              </div>
            )}
          </div>

          {/* Selected for editing */}
          <div className="mb-2">
            <h6 className="fw-semibold" style={{ fontSize: "0.9rem", color: "var(--muted)" }}>Selected for Editing</h6>
          </div>
          <SelectedSection
            title="Audios" icon={<MdAudiotrack size={18} style={{ color: "var(--accent)" }} />}
            ids={selectedAudioIds} lookup={audioMap} type="audio" onRemove={(x) => removeItem("audio", x)}
          />
          <SelectedSection
            title="Images" icon={<MdImage size={18} style={{ color: "var(--accent)" }} />}
            ids={selectedImageIds} lookup={imageMap} type="image" onRemove={(x) => removeItem("image", x)}
          />
          <SelectedSection
            title="Videos" icon={<MdVideocam size={18} style={{ color: "var(--accent)" }} />}
            ids={selectedVideoIds} lookup={videoMap} type="video" onRemove={(x) => removeItem("video", x)}
          />
        </>
      )}

      <div className="mt-3 small" style={{ color: "var(--muted)" }}>
        Created by {project.created_by.name} on {new Date(project.created_at).toLocaleString()}
      </div>
    </div>
  );
}

function SelectedSection({
  title, icon, ids, lookup, type, onRemove,
}: {
  title: string;
  icon: React.ReactNode;
  ids: Set<string>;
  lookup: Map<string, { id: string; title: string; file_url: string | null }>;
  type: "audio" | "image" | "video";
  onRemove: (id: string) => void;
}) {
  const items = [...ids].map((id) => lookup.get(id)).filter(Boolean) as { id: string; title: string; file_url: string | null }[];
  if (items.length === 0) return null;

  return (
    <div className="mb-4">
      <div className="d-flex align-items-center gap-2 mb-2">
        {icon}
        <h6 className="fw-semibold mb-0" style={{ fontSize: "0.85rem" }}>{title}</h6>
        <span className="badge" style={{ background: "var(--surface-2)", color: "var(--muted)", fontSize: "0.65rem" }}>{items.length} selected</span>
      </div>
      <div className="row g-2">
        {items.map((item) => (
          <div key={item.id} className="col-xl-2 col-lg-3 col-md-4 col-sm-6">
            <MediaPreviewCard type={type} title={item.title} fileUrl={item.file_url} onRemove={() => onRemove(item.id)} />
          </div>
        ))}
      </div>
    </div>
  );
}
