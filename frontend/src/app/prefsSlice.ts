import { createSlice, createAsyncThunk, type PayloadAction } from "@reduxjs/toolkit";
import { preferenceService } from "../services/preference.service";

export type ThemeMode = "light" | "dark" | "system";

export interface PrefsState {
  themeMode: ThemeMode;
  themeColor: string;
  sidebarCollapsed: boolean;
}

function applyTheme(mode: ThemeMode, color: string) {
  const dark =
    mode === "dark" || (mode === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
  document.documentElement.style.setProperty("--accent", color);
}

const initialState: PrefsState = {
  themeMode: (localStorage.getItem("theme_mode") as ThemeMode) || "system",
  themeColor: localStorage.getItem("theme_color") || "#6366f1",
  sidebarCollapsed: false,
};

applyTheme(initialState.themeMode, initialState.themeColor);

export const loadPreferences = createAsyncThunk("prefs/load", async () => {
  const pref = await preferenceService.get();
  return pref;
});

export const savePreferences = createAsyncThunk(
  "prefs/save",
  async ({ theme_mode, theme_color }: { theme_mode: string; theme_color: string }) => {
    return await preferenceService.update({ theme_mode, theme_color });
  },
);

const prefsSlice = createSlice({
  name: "prefs",
  initialState,
  reducers: {
    setThemeMode(state, action: PayloadAction<ThemeMode>) {
      state.themeMode = action.payload;
      localStorage.setItem("theme_mode", action.payload);
      applyTheme(action.payload, state.themeColor);
    },
    setThemeColor(state, action: PayloadAction<string>) {
      state.themeColor = action.payload;
      localStorage.setItem("theme_color", action.payload);
      applyTheme(state.themeMode, action.payload);
    },
    toggleSidebar(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadPreferences.fulfilled, (state, action) => {
        const mode = (action.payload.theme_mode as ThemeMode) || "system";
        const color = action.payload.theme_color || "#6366f1";
        state.themeMode = mode;
        state.themeColor = color;
        localStorage.setItem("theme_mode", mode);
        localStorage.setItem("theme_color", color);
        applyTheme(mode, color);
      });
  },
});

export const { setThemeMode, setThemeColor, toggleSidebar } = prefsSlice.actions;
export default prefsSlice.reducer;
