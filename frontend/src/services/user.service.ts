import api from "./api";
import type { Paginated, User } from "../types";

export const userService = {
  async list(page = 1, size = 20): Promise<Paginated<User>> {
    const res = await api.get<Paginated<User>>("/users", { params: { page, size } });
    return res.data;
  },

  async create(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role?: string;
  }): Promise<User> {
    const res = await api.post<User>("/users", data);
    return res.data;
  },

  async deactivate(userId: string): Promise<User> {
    const res = await api.patch<User>(`/users/${userId}/deactivate`);
    return res.data;
  },
};
