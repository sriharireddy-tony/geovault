import api from "./api";
import type { UserPreference } from "../types";

export const preferenceService = {
  async get(): Promise<UserPreference> {
    const res = await api.get<UserPreference>("/preferences");
    return res.data;
  },
  async update(data: { theme_mode: string; theme_color: string }): Promise<UserPreference> {
    const res = await api.put<UserPreference>("/preferences", data);
    return res.data;
  },
};
