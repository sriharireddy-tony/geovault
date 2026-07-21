import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button, Modal, Form, Spinner, Pagination, OverlayTrigger, Tooltip, ProgressBar } from "react-bootstrap";
import { MdDelete, MdPlayArrow, MdStop, MdAudiotrack, MdUpload } from "react-icons/md";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import ConfirmModal from "../../components/common/ConfirmModal";
import ProjectFilterSidebar from "../../components/common/ProjectFilterSidebar";
import { mediaService } from "../../services/media.service";
import type { Audio } from "../../types";
import { formatDate } from "../../utils";

const LANGUAGES = [
  { code: "en-IN", label: "English (India)" },
  { code: "hi-IN", label: "Hindi" },
  { code: "ta-IN", label: "Tamil" },
  { code: "te-IN", label: "Telugu" },
  { code: "kn-IN", label: "Kannada" },
  { code: "ml-IN", label: "Malayalam" },
  { code: "mr-IN", label: "Marathi" },
  { code: "bn-IN", label: "Bengali" },
  { code: "gu-IN", label: "Gujarati" },
  { code: "pa-IN", label: "Punjabi" },
  { code: "od-IN", label: "Odia" },
];

const SPEAKERS = [
  "shubh", "aditya", "ritu", "priya", "neha", "rahul", "pooja",
  "rohan", "simran", "kavya", "amit", "dev", "ishita", "shreya",
];

export default function AudiosPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Audio[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [prompt, setPrompt] = useState("");
  const [language, setLanguage] = useState("en-IN");
  const [speaker, setSpeaker] = useState("shubh");
  const [creating, setCreating] = useState(false);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [filterProject, setFilterProject] = useState("");
  const [filterProjectName, setFilterProjectName] = useState("");
  const [importing, setImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  const importRef = useRef<HTMLInputElement>(null);

  const isAllSelected = filterProject === "";
  const effectiveProjectId = filterProject === "others" ? null : filterProject || null;

  useEffect(() => {
    const el = new window.Audio();
    audioRef.current = el;
    const onEnded = () => setPlayingId(null);
    el.addEventListener("ended", onEnded);
    return () => { el.removeEventListener("ended", onEnded); el.pause(); };
  }, []);

  const togglePlay = (e: React.MouseEvent, item: Audio) => {
    e.stopPropagation();
    const el = audioRef.current;
    if (!el) return;
    if (playingId === item.id) { el.pause(); setPlayingId(null); return; }
    if (item.file_url) { el.src = item.file_url; el.play(); setPlayingId(item.id); }
  };

  const load = useCallback(async (p: number, projId: string) => {
    setLoading(true);
    try {
      const res = await mediaService.listAudios(p, 20, projId);
      setItems(res.items);
      setPages(res.pages);
      setPage(res.page);
    } catch {
      toast.error("Failed to load audios");
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
      const audio = await mediaService.createAudio({
        title, prompt: prompt || null, language, speaker,
        project_id: effectiveProjectId,
      });
      toast.success("Audio generated!");
      setShowCreate(false);
      setTitle(""); setPrompt(""); setLanguage("en-IN"); setSpeaker("shubh");
      navigate(`/audios/${audio.id}`);
    } catch {
      toast.error("Failed to create audio");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      if (playingId === deleteId) { audioRef.current?.pause(); setPlayingId(null); }
      await mediaService.deleteAudio(deleteId);
      toast.success("Audio deleted");
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

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length || !effectiveProjectId) return;
    setImporting(true);
    setImportProgress(0);
    try {
      await mediaService.importAudios([...files], effectiveProjectId, setImportProgress);
      toast.success(`${files.length} audio(s) imported!`);
      load(1, filterProject);
    } catch {
      toast.error("Import failed");
    } finally {
      setImporting(false);
      setImportProgress(0);
      if (importRef.current) importRef.current.value = "";
    }
  };

  const actionBtns = (
    <div className="d-flex align-items-center gap-2">
      <input ref={importRef} type="file" accept="audio/*" multiple hidden onChange={handleImport} />
      <Button variant="outline-secondary" size="sm" onClick={() => importRef.current?.click()} disabled={isAllSelected || importing}>
        <MdUpload size={16} className="me-1" /> Import
      </Button>
      <Button className="btn-accent" onClick={() => setShowCreate(true)} disabled={isAllSelected}>
        + Generate Audio
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
            <h1 className="page-title">Audios</h1>
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
            <MdAudiotrack size={48} className="mb-2" style={{ opacity: 0.3 }} />
            <p className="mb-0">No audios found for this project.</p>
          </div>
        ) : (
          <>
            <div className="row g-3">
              {items.map((item) => (
                <div key={item.id} className="col-sm-6 col-lg-4">
                  <div className="card-custom" onClick={() => navigate(`/audios/${item.id}`)}>
                    <button className="card-custom-delete" onClick={(e) => { e.stopPropagation(); setDeleteId(item.id); }} title="Delete"><MdDelete size={14} /></button>
                    <div className="card-custom-body">
                      <div className="d-flex align-items-center gap-2">
                        {item.file_url ? (
                          <button className={`card-play-btn${playingId === item.id ? " playing" : ""}`} onClick={(e) => togglePlay(e, item)} title={playingId === item.id ? "Stop" : "Play"}>
                            {playingId === item.id ? <MdStop size={16} /> : <MdPlayArrow size={16} />}
                          </button>
                        ) : (
                          <div className="card-play-btn" style={{ background: "var(--surface-2)", color: "var(--muted)", cursor: "default" }}><MdAudiotrack size={14} /></div>
                        )}
                        <div className="card-custom-title" title={item.title}>{item.title}</div>
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

      <Modal show={showCreate} onHide={() => setShowCreate(false)} centered size="lg">
        <Modal.Header closeButton><Modal.Title>Generate Audio (Sarvam AI TTS)</Modal.Title></Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
            <div className="mb-3 p-2 rounded" style={{ background: "var(--surface-2)", fontSize: "0.8rem" }}>
              <strong>Project:</strong> {contextLabel}
            </div>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Title</Form.Label>
              <Form.Control value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="My audio clip" />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label className="small fw-medium">Text to convert to speech</Form.Label>
              <Form.Control as="textarea" rows={4} value={prompt} onChange={(e) => setPrompt(e.target.value)} required placeholder="Enter text here (max 2500 chars)..." maxLength={2500} />
              <Form.Text className="text-muted">{prompt.length}/2500 characters</Form.Text>
            </Form.Group>
            <div className="row">
              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label className="small fw-medium">Language</Form.Label>
                  <Form.Select value={language} onChange={(e) => setLanguage(e.target.value)}>
                    {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
                  </Form.Select>
                </Form.Group>
              </div>
              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label className="small fw-medium">Voice</Form.Label>
                  <Form.Select value={speaker} onChange={(e) => setSpeaker(e.target.value)}>
                    {SPEAKERS.map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </Form.Select>
                </Form.Group>
              </div>
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button type="submit" className="btn-accent" disabled={creating}>
              {creating ? <><Spinner size="sm" className="me-1" /> Generating...</> : "Generate Audio"}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <ConfirmModal show={!!deleteId} message="Delete this audio?" onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />
    </div>
  );
}
