/// <reference types="vite/client" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
<<<<<<< HEAD
import path from 'path';
=======
>>>>>>> origin/main

export default defineConfig(() => {
  return {
    plugins: [react()],
    resolve: {
      alias: {
<<<<<<< HEAD
        '@': path.resolve(__dirname, './src'),
=======
        '@/': new URL('./src/', import.meta.url).pathname,
>>>>>>> origin/main
      },
    },
    envDir: 'src/environments/',
    build: {
      target: 'esnext',
      assetsDir: 'assets',
    },
  };
<<<<<<< HEAD
});
=======
});
>>>>>>> origin/main
