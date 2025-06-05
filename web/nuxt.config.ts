// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  app: {
  },
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: [
    '@nuxt/content',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/scripts',
    '@nuxt/test-utils',
    '@nuxt/ui',
    '@nuxtjs/tailwindcss'
  ],
  css: ['~/assets/css/main.css'],
  vite: {
    plugins: [
      tailwindcss(),
    ],
    build: {
      rollupOptions: {
        output: {
          assetFileNames: 'my-nuxt-site/assets/[name]-[hash][extname]'
        }
      }
    }
  },
  tailwindcss: {
    configPath: '~/tailwind.config.js',
    exposeConfig: false,
    cssPath: '~/assets/css/main.css',
    viewer: true,
  },
})