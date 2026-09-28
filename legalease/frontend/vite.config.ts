import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
    // The frontend calls the API directly at VITE_API_URL so that CORS is
    // genuinely exercised in development. No proxy is configured on purpose.
  },
  build: {
    target: 'es2023',
    sourcemap: false,
    rolldownOptions: {
      output: {
        // Keep the big, rarely-changing libraries in their own long-lived
        // chunks so a UI change does not invalidate all of them.
        advancedChunks: {
          groups: [
            { name: 'react', test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/ },
            {
              name: 'motion',
              test: /node_modules[\\/](framer-motion|motion-dom|motion-utils)[\\/]/,
            },
            { name: 'radix', test: /node_modules[\\/]@radix-ui[\\/]/ },
            { name: 'query', test: /node_modules[\\/]@tanstack[\\/]/ },
            { name: 'net', test: /node_modules[\\/](axios|follow-redirects|form-data)[\\/]/ },
          ],
        },
      },
    },
  },
})
