import api from "./api";
import type { Paginated, Project, ProjectDetail, MessageResponse } from "../types";

export const projectService = {
  async list(page = 1, size = 20): Promise<Paginated<Project>> {
    const res = await api.get<Paginated<Project>>("/projects", { params: { page, size } });
    return res.data;
  },
  async get(id: string): Promise<ProjectDetail> {
    const res = await api.get<ProjectDetail>(`/projects/${id}`);
    return res.data;
  },
  async create(data: { title: string; assets?: { asset_type: string; asset_id: string }[] }): Promise<Project> {
    const res = await api.post<Project>("/projects", data);
    return res.data;
  },
  async update(
    id: string,
    data: { title?: string; assets?: { asset_type: string; asset_id: string }[] },
  ): Promise<Project> {
    const res = await api.put<Project>(`/projects/${id}`, data);
    return res.data;
  },
  async updateSelection(
    id: string,
    data: { audio_ids: string[]; image_ids: string[]; video_ids: string[] },
  ): Promise<ProjectDetail> {
    const res = await api.put<ProjectDetail>(`/projects/${id}/selection`, data);
    return res.data;
  },
  async exportProject(id: string): Promise<MessageResponse> {
    const res = await api.post<MessageResponse>(`/projects/${id}/export`);
    return res.data;
  },
  async delete(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/projects/${id}`);
    return res.data;
  },
};
