import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The FastAPI backend has no CORS middleware, so in development the
// browser talks to Vite (same origin) and Vite forwards /api/* to FastAPI.
// Change the target if your backend runs somewhere else.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
