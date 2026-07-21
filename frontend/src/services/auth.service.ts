import api from "./api";
import type { Token, User, SignupPayload } from "../types";

export const authService = {
  async signup(data: SignupPayload): Promise<Token> {
    const res = await api.post<Token>("/auth/signup", data);
    return res.data;
  },

  async login(email: string, password: string): Promise<Token> {
    const params = new URLSearchParams();
    params.set("username", email);
    params.set("password", password);
    const res = await api.post<Token>("/auth/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return res.data;
  },

  async me(): Promise<User> {
    const res = await api.get<User>("/auth/me");
    return res.data;
  },

  async updateProfile(data: { first_name?: string; last_name?: string; password?: string }): Promise<User> {
    const res = await api.put<User>("/auth/profile", data);
    return res.data;
  },
};
