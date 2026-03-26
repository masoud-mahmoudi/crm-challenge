import { resolve } from 'node:path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, '');

  return {
    root: __dirname,
    cacheDir: '../../node_modules/.vite/apps/web-app',
    plugins: [tailwindcss(), react(), tsconfigPaths({ root: resolve(__dirname, '../..') })],
    server: {
      host: env.VITE_WEB_APP_HOST || '0.0.0.0',
      port: Number(env.VITE_WEB_APP_PORT || 4200),
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true
        },
        '/graphql': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    preview: {
      host: env.VITE_WEB_APP_HOST || '0.0.0.0',
      port: Number(env.VITE_WEB_APP_PREVIEW_PORT || 4300)
    },
    build: {
      outDir: '../../dist/apps/web-app',
      emptyOutDir: true
    },
    test: {
      environment: 'jsdom',
      globals: false,
      setupFiles: ['./src/test/setup.ts']
    }
  };
});