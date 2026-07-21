import api from "./api";
import type { Audio, ImageAsset, Video, Paginated, MessageResponse } from "../types";

export const mediaService = {
  async listAudios(page = 1, size = 20, projectId?: string | null): Promise<Paginated<Audio>> {
    const params: Record<string, unknown> = { page, size };
    if (projectId) params.project_id = projectId;
    const res = await api.get<Paginated<Audio>>("/audios", { params });
    return res.data;
  },
  async createAudio(data: { title: string; prompt?: string | null; language?: string; speaker?: string; project_id?: string | null }): Promise<Audio> {
    const res = await api.post<Audio>("/audios", data);
    return res.data;
  },
  async updateAudio(id: string, data: { project_ids: string[] }): Promise<Audio> {
    const res = await api.put<Audio>(`/audios/${id}`, data);
    return res.data;
  },
  async deleteAudio(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/audios/${id}`);
    return res.data;
  },
  async importAudios(files: File[], projectId: string, onProgress?: (pct: number) => void): Promise<Audio[]> {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    fd.append("project_id", projectId);
    const res = await api.post<Audio[]>("/audios/import", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => { if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total)); },
    });
    return res.data;
  },

  async listImages(page = 1, size = 20, projectId?: string | null): Promise<Paginated<ImageAsset>> {
    const params: Record<string, unknown> = { page, size };
    if (projectId) params.project_id = projectId;
    const res = await api.get<Paginated<ImageAsset>>("/images", { params });
    return res.data;
  },
  async createImage(data: { title: string; prompt?: string | null; project_id?: string | null }): Promise<ImageAsset> {
    const res = await api.post<ImageAsset>("/images", data);
    return res.data;
  },
  async updateImage(id: string, data: { project_ids: string[] }): Promise<ImageAsset> {
    const res = await api.put<ImageAsset>(`/images/${id}`, data);
    return res.data;
  },
  async deleteImage(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/images/${id}`);
    return res.data;
  },
  async importImages(files: File[], projectId: string, onProgress?: (pct: number) => void): Promise<ImageAsset[]> {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    fd.append("project_id", projectId);
    const res = await api.post<ImageAsset[]>("/images/import", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => { if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total)); },
    });
    return res.data;
  },

  async listVideos(page = 1, size = 20, projectId?: string | null): Promise<Paginated<Video>> {
    const params: Record<string, unknown> = { page, size };
    if (projectId) params.project_id = projectId;
    const res = await api.get<Paginated<Video>>("/videos", { params });
    return res.data;
  },
  async createVideo(data: { title: string; prompt?: string | null; project_id?: string | null }): Promise<Video> {
    const res = await api.post<Video>("/videos", data);
    return res.data;
  },
  async updateVideo(id: string, data: { project_ids: string[] }): Promise<Video> {
    const res = await api.put<Video>(`/videos/${id}`, data);
    return res.data;
  },
  async deleteVideo(id: string): Promise<MessageResponse> {
    const res = await api.delete<MessageResponse>(`/videos/${id}`);
    return res.data;
  },
  async importVideos(files: File[], projectId: string, onProgress?: (pct: number) => void): Promise<Video[]> {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    fd.append("project_id", projectId);
    const res = await api.post<Video[]>("/videos/import", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => { if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total)); },
    });
    return res.data;
  },
};
