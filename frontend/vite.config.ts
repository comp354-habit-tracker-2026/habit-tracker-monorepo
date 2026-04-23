/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(() => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    envDir: 'src/environments/',
    server: {
      proxy: {
        '/api/v1/': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
      port: 3000,
    },
    build: {
      target: 'esnext',
      assetsDir: 'assets',
    },
  };
});
