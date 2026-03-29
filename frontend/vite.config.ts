/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { fileURLToPath, URL } from 'node:url'; // Import to resolve paths machine agnostically i.e. windows, mac, ...

export default defineConfig(() => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    envDir: 'src/environments/',
    build: {
      target: 'esnext',
      assetsDir: 'assets',
    },
  };
});