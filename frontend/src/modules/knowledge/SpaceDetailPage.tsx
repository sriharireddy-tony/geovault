import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Modal, Form, Spinner, Badge, ProgressBar } from "react-bootstrap";
import { MdArrowBack, MdUpload, MdRefresh, MdDelete, MdChat, MdNotes } from "react-icons/md";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import {
  knowledgeService,
  type KnowledgeSpace,
  type KnowledgeSource,
} from "../../services/knowledge.service";

const STATUS_COLOR: Record<string, string> = {
  READY: "#10b981",
  FAILED: "#ef4444",
  PROCESSING: "#f59e0b",
  EXTRACTING: "#f59e0b",
  CHUNKING: "#f59e0b",
  EMBEDDING: "#f59e0b",
  INDEXING: "#f59e0b",
  CREATED: "#64748b",
  UPLOADING: "#64748b",
};

export default function SpaceDetailPage() {
  const { spaceId } = useParams<{ spaceId: string }>();
  const navigate = useNavigate();
  const [space, setSpace] = useState<KnowledgeSpace | null>(null);
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showText, setShowText] = useState(false);
  const [textName, setTextName] = useState("");
  const [textContent, setTextContent] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    if (!spaceId) return;
    try {
      const [s, src] = await Promise.all([
        knowledgeService.getSpace(spaceId),
        knowledgeService.listSources(spaceId),
      ]);
      setSpace(s);
      setSources(src.items);
    } catch {
      toast.error("Failed to load space");
      navigate("/knowledge");
    } finally {
      setLoading(false);
    }
  }, [spaceId, navigate]);

  useEffect(() => { load(); }, [load]);

  // Poll while any source is processing
  useEffect(() => {
    const busy = sources.some((s) => !["READY", "FAILED", "DELETED"].includes(s.status));
    if (!busy) return;
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [sources, load]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length || !spaceId) return;
    setUploading(true);
    try {
      for (const f of files) {
        await knowledgeService.uploadSource(spaceId, f);
      }
      toast.success(`${files.length} file(s) uploaded — processing started`);
      load();
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleTextCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!spaceId) return;
    setUploading(true);
    try {
      await knowledgeService.createTextSource(spaceId, { name: textName, content: textContent });
      toast.success("Text source created");
      setShowText(false);
      setTextName("");
      setTextContent("");
      load();
    } catch {
      toast.error("Failed to create text source");
    } finally {
      setUploading(false);
    }
  };

  if (loading || !space) return <Loader />;

  return (
    <div>
      <div className="page-header">
        <div className="d-flex align-items-center gap-2" style={{ minWidth: 0 }}>
          <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate("/knowledge")}>
            <MdArrowBack size={22} />
          </Button>
          <div style={{ minWidth: 0 }}>
            <h1 className="page-title" title={space.title}>{space.title}</h1>
            {space.description && <small style={{ color: "var(--muted)" }}>{space.description}</small>}
          </div>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          <input ref={fileRef} type="file" accept=".txt,.md,.markdown,.pdf,.docx,.csv,.xlsx,.png,.jpg,.jpeg,.webp,.gif" multiple hidden onChange={handleUpload} />
          <Button variant="outline-secondary" size="sm" onClick={() => setShowText(true)}>
            <MdNotes size={16} className="me-1" /> Add Text
          </Button>
          <Button variant="outline-secondary" size="sm" disabled={uploading} onClick={() => fileRef.current?.click()}>
            <MdUpload size={16} className="me-1" /> {uploading ? "Uploading…" : "Upload"}
          </Button>
          <Button className="btn-accent" size="sm" onClick={() => navigate(`/knowledge/${spaceId}/chat`)}>
            <MdChat size={16} className="me-1" /> Chat
          </Button>
        </div>
      </div>

      {uploading && <ProgressBar animated now={100} className="mb-3" style={{ height: 4 }} />}

      {sources.length === 0 ? (
        <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
          <p className="mb-0">No sources yet. Upload PDF, DOCX, CSV, images, TXT/MD or add raw text.</p>
        </div>
      ) : (
        <div className="row g-3">
          {sources.map((s) => (
            <div key={s.id} className="col-md-6">
              <div className="stat-card">
                <div className="d-flex justify-content-between align-items-start gap-2">
                  <div style={{ minWidth: 0 }}>
                    <div className="fw-semibold text-truncate" title={s.name}>{s.name}</div>
                    <div className="small" style={{ color: "var(--muted)" }}>{s.type}</div>
                  </div>
                  <Badge bg="" style={{ background: `${STATUS_COLOR[s.status] ?? "#64748b"}22`, color: STATUS_COLOR[s.status] ?? "#64748b" }}>
                    {s.status}
                  </Badge>
                </div>
                {s.error_message && <div className="small text-danger mt-2">{s.error_message}</div>}
                <div className="d-flex gap-2 mt-3">
                  {s.status === "FAILED" && (
                    <Button size="sm" variant="outline-secondary" onClick={async () => { await knowledgeService.retrySource(s.id); load(); }}>
                      <MdRefresh size={14} /> Retry
                    </Button>
                  )}
                  <Button size="sm" variant="outline-danger" onClick={async () => { await knowledgeService.deleteSource(s.id); load(); }}>
                    <MdDelete size={14} />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal show={showText} onHide={() => setShowText(false)} centered size="lg">
        <Modal.Header closeButton><Modal.Title>Add Text Source</Modal.Title></Modal.Header>
        <Form onSubmit={handleTextCreate}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Name</Form.Label>
              <Form.Control value={textName} onChange={(e) => setTextName(e.target.value)} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Content</Form.Label>
              <Form.Control as="textarea" rows={8} value={textContent} onChange={(e) => setTextContent(e.target.value)} required />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowText(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={uploading}>{uploading ? <Spinner size="sm" /> : "Add"}</Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
}
