import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Spinner } from "react-bootstrap";
import { MdArrowBack, MdImage, MdDownload } from "react-icons/md";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ProjectSelectorDropdown from "../../components/common/ProjectSelectorDropdown";
import { mediaService } from "../../services/media.service";
import type { ImageAsset } from "../../types";

export default function ImageDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [image, setImage] = useState<ImageAsset | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [updating, setUpdating] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await mediaService.listImages(1, 100);
      const found = res.items.find((i) => i.id === id);
      if (!found) { toast.error("Image not found"); navigate("/images"); return; }
      setImage(found);
      setSelectedProjects(found.project_ids ?? []);
    } catch {
      toast.error("Failed to load image");
      navigate("/images");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { load(); }, [load]);

  const handleUpdate = async () => {
    if (!id) return;
    setUpdating(true);
    try {
      const updated = await mediaService.updateImage(id, { project_ids: selectedProjects });
      setImage(updated);
      setSelectedProjects(updated.project_ids ?? []);
      toast.success("Projects updated");
    } catch {
      toast.error("Failed to update");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <Loader />;
  if (!image) return null;

  const promptLines = image.prompt?.split("\n").filter((l) => l.trim()) ?? [];
  const orig = (image.project_ids ?? []).slice().sort().join(",");
  const curr = selectedProjects.slice().sort().join(",");
  const changed = orig !== curr;

  return (
    <div>
      <div className="page-header">
        <div className="d-flex align-items-center gap-2">
          <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate("/images")}>
            <MdArrowBack size={22} />
          </Button>
          <h1 className="page-title" title={image.title}>{image.title}</h1>
        </div>
        <div className="d-flex align-items-center gap-2">
          <ProjectSelectorDropdown value={selectedProjects} onChange={setSelectedProjects} disabled={updating} />
          <Button className="btn-accent" size="sm" disabled={!changed || updating} onClick={handleUpdate}>
            {updating ? <Spinner size="sm" /> : "Update"}
          </Button>
        </div>
      </div>

      <div className="stat-card mb-4">
        {image.file_url ? (
          <div>
            <div className="d-flex align-items-center justify-content-between mb-3">
              <div className="d-flex align-items-center gap-2">
                <MdImage size={20} style={{ color: "var(--accent)" }} />
                <span className="fw-semibold">Image Preview</span>
              </div>
              <a href={image.file_url} download title="Download image" className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1">
                <MdDownload size={16} /> Download
              </a>
            </div>
            <img src={image.file_url} alt={image.title} className="w-100 rounded" style={{ maxHeight: 400, objectFit: "contain" }} />
          </div>
        ) : (
          <div className="text-center py-3" style={{ color: "var(--muted)" }}>
            <MdImage size={32} className="mb-1" style={{ opacity: 0.4 }} />
            <p className="mb-0 small">No image file generated yet</p>
          </div>
        )}
      </div>

      {image.prompt && (
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
