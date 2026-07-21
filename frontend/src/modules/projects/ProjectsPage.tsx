import { useCallback, useEffect, useState } from "react";
import { Button, Modal, Form, Spinner, Pagination, Badge } from "react-bootstrap";
import { MdDelete, MdFolder, MdAudiotrack, MdImage, MdVideocam, MdDownload } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ConfirmModal from "../../components/common/ConfirmModal";
import { projectService } from "../../services/project.service";
import type { Project } from "../../types";
import { formatDate } from "../../utils";

export default function ProjectsPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Project[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  const load = useCallback(async (p: number) => {
    setLoading(true);
    try {
      const res = await projectService.list(p);
      setItems(res.items);
      setPages(res.pages);
      setPage(res.page);
    } catch {
      toast.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(1); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const project = await projectService.create({ title });
      toast.success("Project created!");
      setShowCreate(false);
      setTitle("");
      navigate(`/projects/${project.id}`);
    } catch {
      toast.error("Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await projectService.delete(deleteId);
      toast.success("Project deleted");
      setDeleteId(null);
      load(page);
    } catch {
      toast.error("Failed to delete");
    }
  };

  const [exportingId, setExportingId] = useState<string | null>(null);

  const handleExport = async (e: React.MouseEvent, item: Project) => {
    e.stopPropagation();
    setExportingId(item.id);
    try {
      const res = await projectService.exportProject(item.id);
      toast.success(res.detail);
    } catch {
      toast.error("Export failed");
    } finally {
      setExportingId(null);
    }
  };

  const countAssets = (p: Project, type: string) => p.assets.filter((a) => a.asset_type === type).length;

  if (loading) return <Loader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Projects</h1>
        <Button className="btn-accent" onClick={() => setShowCreate(true)}>+ New Project</Button>
      </div>

      {items.length === 0 ? (
        <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
          <MdFolder size={48} className="mb-2" style={{ opacity: 0.3 }} />
          <p className="mb-0">No projects yet. Click "+ New Project" to create one.</p>
        </div>
      ) : (
        <>
          <div className="row g-3">
            {items.map((item) => (
              <div key={item.id} className="col-sm-6 col-md-4 col-lg-3">
                <div className="card-custom" onClick={() => navigate(`/projects/${item.id}`)}>
                  <div className="card-custom-actions">
                    <button
                      className="card-action-btn"
                      onClick={(e) => handleExport(e, item)}
                      title="Download project files"
                      disabled={exportingId === item.id}
                    >
                      {exportingId === item.id ? <Spinner size="sm" animation="border" style={{ width: 12, height: 12 }} /> : <MdDownload size={14} />}
                    </button>
                    <button
                      className="card-action-btn card-action-btn-danger"
                      onClick={(e) => { e.stopPropagation(); setDeleteId(item.id); }}
                      title="Delete"
                    >
                      <MdDelete size={14} />
                    </button>
                  </div>

                  <div className="card-custom-body">
                    <div className="card-custom-icon" style={{ background: "#0ea5e918", color: "#0ea5e9" }}>
                      <MdFolder size={22} />
                    </div>
                    <div className="card-custom-title" title={item.title}>{item.title}</div>
                    <div className="d-flex gap-2 mt-2 flex-wrap">
                      <Badge bg="" className="d-flex align-items-center gap-1" style={{ background: "var(--surface-2)", color: "var(--text)", fontWeight: 500, fontSize: "0.7rem" }}>
                        <MdAudiotrack size={12} /> {countAssets(item, "audio")}
                      </Badge>
                      <Badge bg="" className="d-flex align-items-center gap-1" style={{ background: "var(--surface-2)", color: "var(--text)", fontWeight: 500, fontSize: "0.7rem" }}>
                        <MdImage size={12} /> {countAssets(item, "image")}
                      </Badge>
                      <Badge bg="" className="d-flex align-items-center gap-1" style={{ background: "var(--surface-2)", color: "var(--text)", fontWeight: 500, fontSize: "0.7rem" }}>
                        <MdVideocam size={12} /> {countAssets(item, "video")}
                      </Badge>
                    </div>
                  </div>
                  <div className="card-custom-footer">
                    <span title={item.created_by.name}>{item.created_by.name}</span>
                    <span>{formatDate(item.created_at)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {pages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Pagination size="sm" className="mb-0">
                <Pagination.Prev disabled={page <= 1} onClick={() => load(page - 1)} />
                {Array.from({ length: Math.min(pages, 7) }, (_, i) => i + 1).map((p) => (
                  <Pagination.Item key={p} active={p === page} onClick={() => load(p)}>{p}</Pagination.Item>
                ))}
                {pages > 7 && <Pagination.Ellipsis disabled />}
                <Pagination.Next disabled={page >= pages} onClick={() => load(page + 1)} />
              </Pagination>
            </div>
          )}
        </>
      )}

      <Modal show={showCreate} onHide={() => setShowCreate(false)} centered>
        <Modal.Header closeButton><Modal.Title>New Project</Modal.Title></Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Title</Form.Label>
              <Form.Control value={title} onChange={(e) => setTitle(e.target.value)} required />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={creating}>{creating ? <Spinner size="sm" /> : "Create"}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <ConfirmModal show={!!deleteId} message="Delete this project?" onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />
    </div>
  );
}
