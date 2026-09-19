/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#08142c',
          navy: '#0b1d3a',
          sidebar: '#0c2044',
          accent: '#1877f2',
          card: '#ffffff',
          bg: '#f1f5f9',
          green: '#10b981',
          amber: '#f59e0b',
          red: '#ef4444',
          purple: '#6366f1',
        }
      }
    },
  },
  plugins: [],
}
