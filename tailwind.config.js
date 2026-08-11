/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f2f9f5',
          100: '#e2f2e7',
          200: '#c5e5d1',
          300: '#99d0b0',
          400: '#69b489',
          500: '#449767',
          600: '#327a51',
          700: '#286241',
          800: '#224e35',
          900: '#1d412d',
          950: '#0f241a',
        },
        accent: {
          gold: '#d97706',   // safety warning amber
          red: '#dc2626',    // high severity red
          emerald: '#059669' // healthy green
        }
      },
    },
  },
  plugins: [],
}
