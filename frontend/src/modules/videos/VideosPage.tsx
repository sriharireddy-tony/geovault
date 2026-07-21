import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button, Modal, Form, Spinner, Pagination, OverlayTrigger, Tooltip, ProgressBar } from "react-bootstrap";
import { MdDelete, MdVideocam, MdUpload } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ConfirmModal from "../../components/common/ConfirmModal";
import ProjectFilterSidebar from "../../components/common/ProjectFilterSidebar";
import { mediaService } from "../../services/media.service";
import type { Video } from "../../types";
import { formatDate } from "../../utils";

export default function VideosPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Video[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [prompt, setPrompt] = useState("");
  const [creating, setCreating] = useState(false);
  const [filterProject, setFilterProject] = useState("");
  const [filterProjectName, setFilterProjectName] = useState("");
  const [importing, setImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  const importRef = useRef<HTMLInputElement>(null);

  const isAllSelected = filterProject === "";
  const effectiveProjectId = filterProject === "others" ? null : filterProject || null;

  const load = useCallback(async (p: number, projId: string) => {
    setLoading(true);
    try {
      const res = await mediaService.listVideos(p, 20, projId);
      setItems(res.items);
      setPages(res.pages);
      setPage(res.page);
    } catch {
      toast.error("Failed to load videos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(1, filterProject); }, [load, filterProject]);

  const handleFilterChange = (id: string, name?: string) => {
    setFilterProject(id);
    setFilterProjectName(name ?? "");
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const vid = await mediaService.createVideo({ title, prompt: prompt || null, project_id: effectiveProjectId });
      toast.success("Video created!");
      setShowCreate(false);
      setTitle(""); setPrompt("");
      navigate(`/videos/${vid.id}`);
    } catch {
      toast.error("Failed to create video");
    } finally {
      setCreating(false);
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length || !effectiveProjectId) return;
    setImporting(true);
    setImportProgress(0);
    try {
      await mediaService.importVideos([...files], effectiveProjectId, setImportProgress);
      toast.success(`${files.length} video(s) imported!`);
      load(1, filterProject);
    } catch {
      toast.error("Import failed");
    } finally {
      setImporting(false);
      setImportProgress(0);
      if (importRef.current) importRef.current.value = "";
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await mediaService.deleteVideo(deleteId);
      toast.success("Video deleted");
      setDeleteId(null);
      load(page, filterProject);
    } catch {
      toast.error("Failed to delete");
    }
  };

  const contextLabel = useMemo(() => {
    if (filterProject === "") return "All Projects";
    if (filterProject === "others") return "Others (no project)";
    return filterProjectName || "Selected Project";
  }, [filterProject, filterProjectName]);

  const actionBtns = (
    <div className="d-flex align-items-center gap-2">
      <input ref={importRef} type="file" accept="video/*" multiple hidden onChange={handleImport} />
      <Button variant="outline-secondary" size="sm" onClick={() => importRef.current?.click()} disabled={isAllSelected || importing}>
        <MdUpload size={16} className="me-1" /> Import
      </Button>
      <Button className="btn-accent" onClick={() => setShowCreate(true)} disabled={isAllSelected}>
        + New Video
      </Button>
    </div>
  );

  return (
    <div className="row g-3">
      <div className="col-12 col-md-3">
        <ProjectFilterSidebar selected={filterProject} onSelect={handleFilterChange} />
      </div>
      <div className="col-12 col-md-9">
        <div className="page-header">
          <div>
            <h1 className="page-title">Videos</h1>
            <small style={{ color: "var(--muted)", fontSize: "0.75rem" }}>{contextLabel}</small>
          </div>
          {isAllSelected ? (
            <OverlayTrigger placement="left" overlay={<Tooltip>Select a project to import or create media</Tooltip>}>
              <span>{actionBtns}</span>
            </OverlayTrigger>
          ) : actionBtns}
        </div>
        {importing && (
          <div className="mb-3">
            <small className="text-muted">Uploading... {importProgress}%</small>
            <ProgressBar now={importProgress} animated striped style={{ height: 6 }} />
          </div>
        )}

        {loading ? <Loader /> : items.length === 0 ? (
          <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
            <MdVideocam size={48} className="mb-2" style={{ opacity: 0.3 }} />
            <p className="mb-0">No videos found for this project.</p>
          </div>
        ) : (
          <>
            <div className="row g-3">
              {items.map((item) => (
                <div key={item.id} className="col-sm-6 col-lg-4">
                  <div className="card-custom" onClick={() => navigate(`/videos/${item.id}`)}>
                    <button className="card-custom-delete" onClick={(e) => { e.stopPropagation(); setDeleteId(item.id); }} title="Delete"><MdDelete size={14} /></button>
                    <div className="card-custom-body">
                      <div className="card-custom-icon" style={{ background: "#f43f5e18", color: "#f43f5e" }}><MdVideocam size={22} /></div>
                      <div className="card-custom-title" title={item.title}>{item.title}</div>
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
                  <Pagination.Prev disabled={page <= 1} onClick={() => load(page - 1, filterProject)} />
                  {Array.from({ length: Math.min(pages, 7) }, (_, i) => i + 1).map((p) => (
                    <Pagination.Item key={p} active={p === page} onClick={() => load(p, filterProject)}>{p}</Pagination.Item>
                  ))}
                  {pages > 7 && <Pagination.Ellipsis disabled />}
                  <Pagination.Next disabled={page >= pages} onClick={() => load(page + 1, filterProject)} />
                </Pagination>
              </div>
            )}
          </>
        )}
      </div>

      <Modal show={showCreate} onHide={() => setShowCreate(false)} centered>
        <Modal.Header closeButton><Modal.Title>New Video</Modal.Title></Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
            <div className="mb-3 p-2 rounded" style={{ background: "var(--surface-2)", fontSize: "0.8rem" }}>
              <strong>Project:</strong> {contextLabel}
            </div>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Title</Form.Label>
              <Form.Control value={title} onChange={(e) => setTitle(e.target.value)} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Prompt</Form.Label>
              <Form.Control as="textarea" rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={creating}>{creating ? <Spinner size="sm" /> : "Create"}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <ConfirmModal show={!!deleteId} message="Delete this video?" onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />
    </div>
  );
}
