import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd() + '/..', '')
  const host = env.APP_HOST || process.env.APP_HOST || '192.168.1.101'
  const port = parseInt(env.FRONTEND_PORT || process.env.FRONTEND_PORT || '5173', 10)
  const backendPort = env.BACKEND_PORT || process.env.BACKEND_PORT || '8000'

  return {
    plugins: [react()],
    server: {
      host: host,
      port: port,
      proxy: {
        '/api': {
          target: `http://${host}:${backendPort}`,
          changeOrigin: true,
        },
      },
    },
  }
})
