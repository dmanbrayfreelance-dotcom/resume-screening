/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        coral: {
          DEFAULT: '#EF8A62',
          50: '#fef6f3',
          100: '#fdebe4',
          200: '#fbd7c8',
          300: '#f6b89f',
          400: '#f29672',
          500: '#EF8A62',
          600: '#e37042',
          700: '#be5329',
          800: '#974324',
          900: '#7b3a22',
          950: '#421b0e',
        },
        cerulean: {
          DEFAULT: '#67A9CF',
          50: '#f2f8fc',
          100: '#e1eff7',
          200: '#c8e2f0',
          300: '#a3cfe6',
          400: '#76b4d8',
          500: '#67A9CF',
          600: '#3d8bb8',
          700: '#327096',
          800: '#2d5e7d',
          900: '#294f68',
          950: '#1a3344',
        },
        offwhite: '#F7F7F7',
        slate: {
          950: '#070b12',
          900: '#0e1726',
          850: '#141f33',
          800: '#1b2943',
          700: '#334155',
        }
      }
    },
  },
  plugins: [],
}
