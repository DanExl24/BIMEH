/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        darkBg: '#0b0f19',
        darkCard: '#151d30',
        darkBorder: '#1f2b45',
        accentCyan: '#06b6d4',
        accentTeal: '#14b8a6',
        accentAmber: '#f59e0b',
        accentRed: '#ef4444',
        accentGreen: '#10b981',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      }
    },
  },
  plugins: [],
}
