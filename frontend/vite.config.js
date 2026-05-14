import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
    fs: {
      // Don't let Vite walk into test output / build artifacts
      deny: ["playwright-report/**", "test-results/**", "dist/**"],
    },
  },
  optimizeDeps: {
    entries: ["index.html"],
  },
});
