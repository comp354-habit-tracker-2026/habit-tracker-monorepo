/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig(() => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
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
    },
    build: {
      target: 'esnext',
      assetsDir: 'assets',
    },
  };
});
