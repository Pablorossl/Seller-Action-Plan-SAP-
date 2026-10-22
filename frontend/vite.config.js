import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/static/react/',
  server: {
    port: 5173,
    strictPort: true,
    proxy: Object.fromEntries(['/api', '/accounts'].map(path => [path, {
      target: 'http://127.0.0.1:8000',
      changeOrigin: false,
    }])),
  },
});
