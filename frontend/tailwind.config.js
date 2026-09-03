/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f4f6f9',
          100: '#e3e8f0',
          400: '#5b6b8c',
          600: '#334063',
          700: '#232f4d',
          800: '#1a2440',
          900: '#131b30',
        },
        gold: {
          50: '#fbf6e9',
          100: '#f3e6c0',
          400: '#c9932f',
          500: '#b8860b',
          600: '#9c710a',
        },
        cream: '#fffdf7',
      },
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        sans: ['"Public Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(19,27,48,0.04), 0 8px 24px -12px rgba(19,27,48,0.12)',
      },
    },
  },
  plugins: [],
}
