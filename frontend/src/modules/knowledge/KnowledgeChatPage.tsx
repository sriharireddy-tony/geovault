import { useCallback, useEffect, useRef, useState } from "react";
import { Button, Form, Spinner, ListGroup } from "react-bootstrap";
import { MdArrowBack, MdSend, MdAdd } from "react-icons/md";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import Loader from "../../components/common/Loader";
import {
  knowledgeService,
  type ChatMessage,
  type Citation,
  type Conversation,
} from "../../services/knowledge.service";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export default function KnowledgeChatPage() {
  const { spaceId } = useParams<{ spaceId: string }>();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadConversation = useCallback(async (conv: Conversation) => {
    setConversation(conv);
    const msgs = await knowledgeService.listMessages(conv.id);
    setMessages(msgs);
  }, []);

  const init = useCallback(async () => {
    if (!spaceId) return;
    try {
      const existing = await knowledgeService.listConversations(spaceId);
      setConversations(existing);
      if (existing.length) {
        await loadConversation(existing[0]);
      } else {
        const conv = await knowledgeService.createConversation({ space_id: spaceId, title: "Chat" });
        setConversations([conv]);
        await loadConversation(conv);
      }
    } catch {
      toast.error("Failed to start chat");
      navigate(`/knowledge/${spaceId}`);
    } finally {
      setLoading(false);
    }
  }, [spaceId, navigate, loadConversation]);

  useEffect(() => { init(); }, [init]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamText]);

  const newChat = async () => {
    if (!spaceId) return;
    const conv = await knowledgeService.createConversation({
      space_id: spaceId,
      title: `Chat ${new Date().toLocaleString()}`,
    });
    setConversations((prev) => [conv, ...prev]);
    setMessages([]);
    setConversation(conv);
  };

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!conversation || !input.trim() || streaming) return;
    const question = input.trim();
    setInput("");
    setStreaming(true);
    setStreamText("");
    setStatus("langgraph");
    setMessages((prev) => [
      ...prev,
      {
        id: `tmp-${Date.now()}`,
        conversation_id: conversation.id,
        role: "user",
        content: question,
        created_at: new Date().toISOString(),
        citations: [],
      },
    ]);

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${API_BASE}/api/v1/knowledge/conversations/${conversation.id}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content: question }),
      });
      if (!res.ok || !res.body) throw new Error("Chat failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let full = "";
      let finalCitations: Citation[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const evt = JSON.parse(line);
            if (evt.type === "status") setStatus(evt.detail);
            if (evt.type === "token") {
              full += evt.content;
              setStreamText(full);
            }
            if (evt.type === "done") {
              finalCitations = evt.citations || [];
            }
            if (evt.type === "error") toast.error(evt.detail);
          } catch { /* ignore */ }
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `asst-${Date.now()}`,
          conversation_id: conversation.id,
          role: "assistant",
          content: full,
          created_at: new Date().toISOString(),
          citations: finalCitations,
        },
      ]);
      setStreamText("");
    } catch {
      toast.error("Chat failed — check Ollama / LangGraph backend");
    } finally {
      setStreaming(false);
      setStatus("");
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="row g-3" style={{ minHeight: "calc(100vh - 120px)" }}>
      <div className="col-md-3">
        <div className="stat-card h-100">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong className="small">Your chats</strong>
            <Button size="sm" variant="outline-secondary" onClick={newChat} title="New chat">
              <MdAdd size={16} />
            </Button>
          </div>
          <ListGroup variant="flush">
            {conversations.map((c) => (
              <ListGroup.Item
                key={c.id}
                action
                active={conversation?.id === c.id}
                onClick={() => loadConversation(c)}
                className="px-2 py-2 small"
                style={{ cursor: "pointer" }}
              >
                <div className="text-truncate" title={c.title}>{c.title}</div>
              </ListGroup.Item>
            ))}
          </ListGroup>
          <div className="small mt-3" style={{ color: "var(--muted)" }}>
            History is saved per user & tenant and restored on login.
          </div>
        </div>
      </div>

      <div className="col-md-9 d-flex flex-column" style={{ height: "calc(100vh - 120px)" }}>
        <div className="page-header mb-3">
          <div className="d-flex align-items-center gap-2">
            <Button variant="link" className="p-0" style={{ color: "var(--muted)" }} onClick={() => navigate(`/knowledge/${spaceId}`)}>
              <MdArrowBack size={22} />
            </Button>
            <h1 className="page-title">AI Chat</h1>
          </div>
          <small style={{ color: "var(--muted)" }}>LangGraph · Guardrails · LangSmith-ready</small>
        </div>

        <div className="flex-grow-1 overflow-auto mb-3 pe-1">
          {messages.map((m) => (
            <div
              key={m.id}
              className="mb-3 p-3 rounded"
              style={{
                background: m.role === "user" ? "var(--surface-2)" : "var(--surface)",
                border: "1px solid var(--border)",
                maxWidth: "92%",
                marginLeft: m.role === "user" ? "auto" : 0,
              }}
            >
              <div className="small fw-semibold mb-1" style={{ color: "var(--muted)" }}>{m.role === "user" ? "You" : "Assistant"}</div>
              <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
              {m.citations?.length > 0 && (
                <div className="mt-2 d-flex flex-wrap gap-1">
                  {m.citations.map((c, i) => (
                    <span key={i} className="badge" style={{ background: "var(--surface-2)", color: "var(--text)", fontWeight: 500 }}>
                      {c.source_name || "Source"}{c.page_number ? ` p.${c.page_number}` : ""}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {streaming && streamText && (
            <div className="mb-3 p-3 rounded" style={{ background: "var(--surface)", border: "1px solid var(--border)", maxWidth: "92%" }}>
              <div className="small fw-semibold mb-1" style={{ color: "var(--muted)" }}>Assistant {status && `(${status})`}</div>
              <div style={{ whiteSpace: "pre-wrap" }}>{streamText}</div>
            </div>
          )}
          {streaming && !streamText && (
            <div className="mb-3" style={{ color: "var(--muted)" }}>
              <Spinner size="sm" className="me-2" /> {status || "Running LangGraph…"}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <Form onSubmit={send} className="d-flex gap-2">
          <Form.Control
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your documents…"
            disabled={streaming}
          />
          <Button type="submit" className="btn-accent" disabled={streaming || !input.trim()}>
            <MdSend size={18} />
          </Button>
        </Form>
      </div>
    </div>
  );
}
