/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

export default defineConfig(() => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@/': new URL('./src/', import.meta.url).pathname,
      },
    },
    envDir: 'src/environments/',
    build: {
      target: 'esnext',
      assetsDir: 'assets',
    },
    server: {
    port: 3000
  },
  };
});
