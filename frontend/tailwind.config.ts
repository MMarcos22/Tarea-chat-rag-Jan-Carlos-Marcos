import type { Config } from 'tailwindcss'
export default <Partial<Config>>{
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue'
  ],
  theme: {
    extend: {
      colors: { brand: { DEFAULT: '#7c4dff' } }
    }
  }
}
