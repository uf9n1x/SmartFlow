import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // Element Plus 组件自动导入
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        // SCSS 全局变量注入
        additionalData: `@use "@/styles/variables" as *;`,
      },
    },
  },
  build: {
    // 提高大文件警告阈值（ECharts 等图表库体积较大属正常）
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      onwarn(warning: { code?: string; message: string }, warn: (w: typeof warning) => void) {
        // 忽略第三方库 @vueuse/core 的 PURE 注释兼容性警告
        if (warning.code === 'INVALID_ANNOTATION') return
        warn(warning)
      },
    },
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
