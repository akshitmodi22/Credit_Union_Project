/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#EBF2FB',
          100: '#C5DAF5',
          200: '#9FC2EE',
          400: '#5A9AE0',
          600: '#387ED1',
          700: '#2B6AB8',
          800: '#1A5FA8',
          900: '#0D3D70',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    }
  },
  plugins: []
}
