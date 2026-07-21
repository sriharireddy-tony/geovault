export type UserRole = "SUPER_ADMIN" | "ADMIN" | "USER";

export interface CreatorInfo {
  id: string;
  name: string;
}

export interface User {
  id: string;
  tenant_id: string | null;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  created_by: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Audio {
  id: string;
  tenant_id: string;
  created_by: CreatorInfo;
  title: string;
  prompt: string | null;
  file_url: string | null;
  project_id: string | null;
  project_ids: string[];
  is_active: boolean;
  created_at: string;
}

export interface ImageAsset {
  id: string;
  tenant_id: string;
  created_by: CreatorInfo;
  title: string;
  prompt: string | null;
  file_url: string | null;
  project_id: string | null;
  project_ids: string[];
  is_active: boolean;
  created_at: string;
}

export interface Video {
  id: string;
  tenant_id: string;
  created_by: CreatorInfo;
  title: string;
  prompt: string | null;
  file_url: string | null;
  project_id: string | null;
  project_ids: string[];
  is_active: boolean;
  created_at: string;
}

export type AssetType = "audio" | "image" | "video";

export interface ProjectAsset {
  id: string;
  project_id: string;
  asset_type: AssetType;
  asset_id: string;
}

export interface Project {
  id: string;
  tenant_id: string;
  created_by: CreatorInfo;
  title: string;
  is_active: boolean;
  created_at: string;
  assets: ProjectAsset[];
}

export interface MediaBucket {
  audios: Audio[];
  images: ImageAsset[];
  videos: Video[];
}

export interface ProjectDetail extends Project {
  available_media: MediaBucket;
  selected_media: MediaBucket;
}

export interface UserPreference {
  id: string;
  user_id: string;
  theme_mode: string;
  theme_color: string;
}

export interface SignupPayload {
  tenant_name: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface MessageResponse {
  detail: string;
}
