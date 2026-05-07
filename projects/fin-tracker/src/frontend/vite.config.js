import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://fin-tracker-backend:8000",
        changeOrigin: true,
      },
    },
    host: "0.0.0.0",
    port: 5173,
    hmr: false,  // Disable HMR in Docker
  },
});
