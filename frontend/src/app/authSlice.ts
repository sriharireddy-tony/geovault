import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { authService } from "../services/auth.service";
import type { User, SignupPayload } from "../types";

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem("access_token"),
  loading: false,
  error: null,
};

export const signup = createAsyncThunk("auth/signup", async (data: SignupPayload, { rejectWithValue }) => {
  try {
    const tokenRes = await authService.signup(data);
    localStorage.setItem("access_token", tokenRes.access_token);
    const user = await authService.me();
    return { token: tokenRes.access_token, user };
  } catch (err: any) {
    return rejectWithValue(err.response?.data?.detail || "Signup failed");
  }
});

export const login = createAsyncThunk(
  "auth/login",
  async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const tokenRes = await authService.login(email, password);
      localStorage.setItem("access_token", tokenRes.access_token);
      const user = await authService.me();
      return { token: tokenRes.access_token, user };
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || "Login failed");
    }
  },
);

export const fetchMe = createAsyncThunk("auth/fetchMe", async (_, { rejectWithValue }) => {
  try {
    return await authService.me();
  } catch (err: any) {
    localStorage.removeItem("access_token");
    return rejectWithValue("Session expired");
  }
});

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.error = null;
      localStorage.removeItem("access_token");
    },
    clearError(state) {
      state.error = null;
    },
    setUser(state, action) {
      state.user = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(signup.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(signup.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(signup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(login.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchMe.pending, (state) => { state.loading = true; })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchMe.rejected, (state) => {
        state.loading = false;
        state.token = null;
        state.user = null;
      });
  },
});

export const { logout, clearError, setUser } = authSlice.actions;
export default authSlice.reducer;
