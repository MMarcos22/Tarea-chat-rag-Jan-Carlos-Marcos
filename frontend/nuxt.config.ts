// frontend/nuxt.config.ts
export default defineNuxtConfig({
  ssr: false,
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/tailwind.css'],    // <-- este archivo debe existir exactamente ahí
  compatibilityDate: '2025-10-14',
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || 'http://localhost:8000'
    }
  }
})
