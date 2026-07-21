import { useCallback, useEffect, useState } from "react";
import { Button, Modal, Form, Spinner } from "react-bootstrap";
import { MdMenuBook, MdDelete, MdChat } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ConfirmModal from "../../components/common/ConfirmModal";
import { knowledgeService, type KnowledgeSpace } from "../../services/knowledge.service";
import { formatDate } from "../../utils";

export default function KnowledgeSpacesPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<KnowledgeSpace[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await knowledgeService.listSpaces(1, 50);
      setItems(res.items);
    } catch {
      toast.error("Failed to load knowledge spaces");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const space = await knowledgeService.createSpace({ title, description: description || undefined });
      toast.success("Knowledge space created");
      setShowCreate(false);
      setTitle("");
      setDescription("");
      navigate(`/knowledge/${space.id}`);
    } catch {
      toast.error("Failed to create space");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await knowledgeService.deleteSpace(deleteId);
      toast.success("Space deleted");
      setDeleteId(null);
      load();
    } catch {
      toast.error("Failed to delete");
    }
  };

  if (loading) return <Loader />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Knowledge</h1>
        <Button className="btn-accent" onClick={() => setShowCreate(true)}>+ New Space</Button>
      </div>

      {items.length === 0 ? (
        <div className="stat-card text-center py-5" style={{ color: "var(--muted)" }}>
          <MdMenuBook size={48} className="mb-2" style={{ opacity: 0.3 }} />
          <p className="mb-0">Create a Knowledge Space to upload documents and chat with AI.</p>
        </div>
      ) : (
        <div className="row g-3">
          {items.map((item) => (
            <div key={item.id} className="col-sm-6 col-md-4 col-lg-3">
              <div className="card-custom" onClick={() => navigate(`/knowledge/${item.id}`)}>
                <button
                  className="card-custom-delete"
                  onClick={(e) => { e.stopPropagation(); setDeleteId(item.id); }}
                  title="Delete"
                >
                  <MdDelete size={14} />
                </button>
                <div className="card-custom-body">
                  <div className="card-custom-icon" style={{ background: "#8b5cf618", color: "#8b5cf6" }}>
                    <MdMenuBook size={22} />
                  </div>
                  <div className="card-custom-title" title={item.title}>{item.title}</div>
                  <div className="small mt-1" style={{ color: "var(--muted)" }}>
                    {item.source_count} source{item.source_count === 1 ? "" : "s"}
                  </div>
                </div>
                <div className="card-custom-footer">
                  <span>{formatDate(item.created_at)}</span>
                  <button
                    className="btn btn-sm btn-link p-0"
                    onClick={(e) => { e.stopPropagation(); navigate(`/knowledge/${item.id}/chat`); }}
                    title="Chat"
                  >
                    <MdChat size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal show={showCreate} onHide={() => setShowCreate(false)} centered>
        <Modal.Header closeButton><Modal.Title>New Knowledge Space</Modal.Title></Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Title</Form.Label>
              <Form.Control value={title} onChange={(e) => setTitle(e.target.value)} required />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Description</Form.Label>
              <Form.Control as="textarea" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={creating}>{creating ? <Spinner size="sm" /> : "Create"}</Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <ConfirmModal show={!!deleteId} message="Delete this knowledge space?" onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />
    </div>
  );
}
