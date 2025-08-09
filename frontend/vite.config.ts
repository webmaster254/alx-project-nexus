import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    // Bundle analyzer for production builds
    ...(process.env.ANALYZE ? [visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    })] : []),
  ],
  define: {
    // Replace process.env variables at build time
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  build: {
    // Production optimizations
    minify: mode === 'production' ? 'esbuild' : false,
    cssMinify: mode === 'production',
    // Enable tree shaking
    rollupOptions: {
      output: {
        // Optimize chunk naming for caching
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        manualChunks: {
          // Vendor chunk for React and related libraries
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI components chunk
          ui: ['lucide-react'],
          // HTTP client chunk
          http: ['axios'],
        },
      },
    },
    // Enable source maps for production debugging (can be disabled for security)
    sourcemap: mode === 'production' ? 'hidden' : true,
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Enable compression
    reportCompressedSize: true,
    // Target modern browsers for smaller bundles
    target: 'es2020',
  },
  // Performance optimizations
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'lucide-react'],
  },
  // Preview server configuration for production testing
  preview: {
    port: 3000,
    host: true,
    strictPort: true,
  },
  // Development server configuration
  server: {
    port: 5173,
    host: true,
    strictPort: true,
  },
}));
