/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    // Recycler polling creates browser timers. A single fork gives every CI
    // run an isolated teardown boundary instead of leaving the runner open.
    pool: 'forks',
    maxWorkers: 1,
    minWorkers: 1,
  },
});
