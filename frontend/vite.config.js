import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The bundle is written into the Django app's static directory and served by
// Django/WhiteNoise as /static/mainapp/dist/... (stable entry names, hashed chunks).
export default defineConfig({
  plugins: [react()],
  base: '/static/mainapp/dist/',
  build: {
    outDir: '../mainapp/static/mainapp/dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        app: 'src/main.jsx',
        admin: 'src/admin.jsx',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: (asset) => (asset.names?.[0]?.endsWith('.css') ? '[name][extname]' : 'assets/[name]-[hash][extname]'),
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.js'],
    restoreMocks: true,
  },
});
