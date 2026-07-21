import api from "./api";
import type { Paginated, MessageResponse } from "../types";

export interface KnowledgeSpace {
  id: string;
  tenant_id: string;
  created_by: string;
  title: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  member_role?: string | null;
  source_count: number;
}

export interface KnowledgeSource {
  id: string;
  tenant_id: string;
  space_id: string;
  created_by: string;
  type: string;
  name: string;
  status: string;
  storage_key: string | null;
  mime_type: string | null;
  byte_size: number | null;
  error_message: string | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  tenant_id: string;
  space_id: string | null;
  created_by: string;
  title: string;
  scope_type: string;
  created_at: string;
}

export interface Citation {
  source_id: string;
  source_name?: string | null;
  chunk_id?: string | null;
  page_number?: number | null;
  snippet?: string | null;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  model?: string | null;
  created_at: string;
  citations: Citation[];
}

export const knowledgeService = {
  async listSpaces(page = 1, size = 20): Promise<Paginated<KnowledgeSpace>> {
    const res = await api.get<Paginated<KnowledgeSpace>>("/knowledge/spaces", { params: { page, size } });
    return res.data;
  },
  async createSpace(data: { title: string; description?: string }): Promise<KnowledgeSpace> {
    const res = await api.post<KnowledgeSpace>("/knowledge/spaces", data);
    return res.data;
  },
  async getSpace(id: string): Promise<KnowledgeSpace> {
    const res = await api.get<KnowledgeSpace>(`/knowledge/spaces/${id}`);
    return res.data;
  },
  async deleteSpace(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/knowledge/spaces/${id}`);
    return res.data;
  },
  async listSources(spaceId: string, page = 1, size = 50): Promise<Paginated<KnowledgeSource>> {
    const res = await api.get<Paginated<KnowledgeSource>>(`/knowledge/spaces/${spaceId}/sources`, { params: { page, size } });
    return res.data;
  },
  async createTextSource(spaceId: string, data: { name: string; content: string; type?: string }): Promise<KnowledgeSource> {
    const res = await api.post<KnowledgeSource>(`/knowledge/spaces/${spaceId}/sources/text`, data);
    return res.data;
  },
  async uploadSource(spaceId: string, file: File, name?: string): Promise<KnowledgeSource> {
    const fd = new FormData();
    fd.append("file", file);
    if (name) fd.append("name", name);
    const res = await api.post<KnowledgeSource>(`/knowledge/spaces/${spaceId}/sources/upload`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },
  async deleteSource(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/knowledge/sources/${id}`);
    return res.data;
  },
  async retrySource(id: string): Promise<KnowledgeSource> {
    const res = await api.post<KnowledgeSource>(`/knowledge/sources/${id}/retry`);
    return res.data;
  },
  async createConversation(data: { space_id: string; title?: string; source_ids?: string[] }): Promise<Conversation> {
    const res = await api.post<Conversation>("/knowledge/conversations", data);
    return res.data;
  },
  async listConversations(spaceId?: string): Promise<Conversation[]> {
    const res = await api.get<Conversation[]>("/knowledge/conversations", { params: spaceId ? { space_id: spaceId } : {} });
    return res.data;
  },
  async listMessages(conversationId: string): Promise<ChatMessage[]> {
    const res = await api.get<ChatMessage[]>(`/knowledge/conversations/${conversationId}/messages`);
    return res.data;
  },
};
