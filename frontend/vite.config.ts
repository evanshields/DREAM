import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// DREAM frontend — built to static assets served same-origin behind Caddy at
// dream.shieldstone.co (/api/* -> :8001, everything else -> the dist/ here).
// In dev, proxy /api to the local FastAPI backend on :8001 so the relative
// '/api' base in api.ts works without CORS gymnastics.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
