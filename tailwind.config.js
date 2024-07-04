/** @type {import('tailwindcss').Config} */
import withMt from '@material-tailwind/html/utils/withMT'
module.exports = withMt({
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
})
