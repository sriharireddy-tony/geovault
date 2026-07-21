import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  css: {
    preprocessorOptions: {
      scss: { api: "modern-compiler", silenceDeprecations: ["import", "global-builtin", "color-functions", "if-function"] },
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true, secure: false },
      "/media": { target: "http://127.0.0.1:8000", changeOrigin: true, secure: false },
    },
  },
});
